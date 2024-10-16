# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import base64
import hashlib
import json
import os
import random

import aiohttp
import socketio
from cryptography.fernet import Fernet

from classquiz.config import redis, settings
from classquiz.db.models import (
    PlayGame,
    QuizQuestionType,
    GameSession,
    GamePlayer,
    QuizQuestion,
    VotingQuizAnswer,
    AnswerDataList,
    AnswerData,
)
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime

from classquiz.socket_server.export_helpers import save_quiz_to_storage

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
settings = settings()


def get_fernet_key() -> bytes:
    hlib = hashlib.sha256()
    hlib.update(settings.secret_key.encode("utf-8"))
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1")[:32])


fernet = Fernet(get_fernet_key())


async def generate_final_results(game_data: PlayGame, game_pin: str) -> dict:
    results = {}
    for i in range(len(game_data.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        if redis_res is None:
            continue
        else:
            results[str(i)] = json.loads(redis_res)
    return results


def calculate_score(z: float, t: int) -> int:
    t = t * 1000
    res = (t - z) / t
    return int(res * 1000)


async def set_answer(answers, game_pin: str, q_index: int, data: AnswerData) -> AnswerDataList:
    if answers is None:
        answers = AnswerDataList(__root__=[data])
    else:
        answers = AnswerDataList.parse_raw(answers)
        answers.__root__.append(data)
    await redis.set(
        f"game_session:{game_pin}:{q_index}",
        answers.json(),
        ex=7200,
    )
    return answers


# Helper function to calculate remaining time
async def calculate_remaining_time(game_pin: str, game_data: PlayGame) -> float | None:
    time_q_started_str = await redis.get(f"game:{game_pin}:current_time")
    if time_q_started_str:
        time_q_started = datetime.fromisoformat(time_q_started_str)
        now = datetime.now()
        elapsed_time = (now - time_q_started).total_seconds()
        max_time = float(game_data.questions[game_data.current_question].time)
        return max_time - elapsed_time
    else:
        return None


async def get_latest_submitted_answer(game_pin: str, username: str, current_question_index: int) -> dict | None:
    """
    Get the latest submitted answer for a given player in the current question.

    Args:
        game_pin (str): The game PIN to identify the game session.
        username (str): The player's username.
        current_question_index (int): The index of the current question.

    Returns:
        dict | None: A dictionary containing the latest submitted answer if found, or None if no answer exists.
    """
    # Fetch answers from Redis for the current question
    answers = await redis.get(f"game_session:{game_pin}:{current_question_index}")

    if answers is not None:
        # Parse the list of answers
        answers = AnswerDataList.parse_raw(answers)
        # Iterate through the answers to find the player's answer
        for answer in answers.__root__:
            if answer.username == username:
                # Return the answer details if found
                return {
                    "question_index": current_question_index,
                    "answer": answer.answer,
                }

    # Return None if no answer is found
    return None


class _JoinGameData(BaseModel):
    username: str
    game_pin: str
    captcha: str | None
    custom_field: str | None


class _RejoinGameData(BaseModel):
    old_sid: str
    game_pin: str
    username: str


@sio.event
async def rejoin_game(sid: str, data: dict):
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
        return

    try:
        data = _RejoinGameData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)

    # Retrieve the player's old SID and check if they were in the game before
    redis_sid_key = f"game_session:{data.game_pin}:players:{data.username}"
    old_sid = await redis.get(redis_sid_key)

    # Ensure the player was already part of the game
    # if old_sid != data.old_sid:
    #    return

    # Sync time and session management
    encrypted_datetime = fernet.encrypt(datetime.now().isoformat().encode("utf-8")).decode("utf-8")
    await sio.emit("time_sync", encrypted_datetime, room=sid)

    # Update the player's session SID in Redis
    await redis.set(redis_sid_key, sid)
    await redis.srem(
        f"game_session:{data.game_pin}:players", GamePlayer(username=data.username, sid=data.old_sid).json()
    )
    await redis.sadd(f"game_session:{data.game_pin}:players", GamePlayer(username=data.username, sid=sid).json())

    # Restore the game state from Redis and send it to the player
    game_data = PlayGame.parse_raw(redis_res)
    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "sid_custom": sid,
        "admin": False,
    }
    await sio.save_session(sid, session)
    await sio.enter_room(sid, data.game_pin)

    latest_answer = await get_latest_submitted_answer(data.game_pin, data.username, game_data.current_question)

    # Send the restored game state to the player
    await sio.emit(
        "rejoined_game",
        {
            **json.loads(game_data.json(exclude={"quiz_id", "questions", "user_id"})),
            "question_count": len(game_data.questions),
            "question_show": game_data.question_show,
            "latest_answer": latest_answer
        },
        room=sid,
    )

    # Restore player score or any other game data if necessary
    player_scores = await redis.hgetall(f"game_session:{data.game_pin}:player_scores")
    if data.username not in player_scores:
        await redis.hset(f"game_session:{data.game_pin}:player_scores", data.username, 0)
    await sio.emit("player_scores", player_scores, room=sid)

    remaining_time = await calculate_remaining_time(data.game_pin, game_data)
    if remaining_time is not None:
        if remaining_time > 0:
            await sio.emit("remaining_time", {"time_left": remaining_time}, room=sid)
        else:
            await sio.emit("time_up", room=sid)
    else:
        print("No question start time found")
        await sio.emit("error", room=sid)


@sio.event
async def join_game(sid: str, data: dict):
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
        return
    try:
        data = _JoinGameData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    game_data = PlayGame.parse_raw(redis_res)

    if game_data.started:
        # Allow late join but emit a warning or set conditions for the player
        await sio.emit("game_already_started_but_allowed", room=sid)
        player_scores = await redis.hgetall(f"game_session:{data.game_pin}:player_scores")
        # Emit current game state and question to late joiners
        print("Joining game late")
        await sio.emit(
            "joined_game_late",
            {
                **json.loads(game_data.json(exclude={"quiz_id", "questions", "user_id"})),
                "current_question": game_data.current_question,
                "question_count": len(game_data.questions),
                "question_show": game_data.question_show,
                "player_scores": player_scores
            },
            room=sid,
        )

        # Send the current question to the late joiner
        current_question = game_data.questions[game_data.current_question]
        if current_question.type == QuizQuestionType.SLIDE:
            await sio.emit("set_question_number", {"question_index": game_data.current_question}, room=sid)
        else:
            await sio.emit(
                "set_question_number",
                {
                    "question_index": game_data.current_question,
                    "question": current_question.dict(),
                    "question_show": game_data.question_show,
                },
                room=sid,
            )

        remaining_time = await calculate_remaining_time(data.game_pin, game_data)
        if remaining_time is not None:
            if remaining_time > 0:
                await sio.emit("remaining_time", {"time_left": remaining_time}, room=sid)
            else:
                await sio.emit("time_up", room=sid)
        else:
            print("No question start time found")
            await sio.emit("error", room=sid)

    # +++ START checking captcha +++
    if game_data.captcha_enabled:
        async with aiohttp.ClientSession() as session:
            try:
                if settings.hcaptcha_key is not None:
                    try:
                        async with session.post(
                            "https://hcaptcha.com/siteverify",
                            data={"response": data.captcha, "secret": settings.hcaptcha_key},
                        ) as resp:
                            resp_data = await resp.json()
                            if not resp_data["success"]:
                                print("CAPTCHA FAILED")
                                return
                    except KeyError:
                        print("CAPTCHA FAILED")
                        return
                elif settings.recaptcha_key is not None:
                    async with session.post(
                        "https://www.google.com/recaptcha/api/siteverify",
                        data={"secret": settings.recaptcha_key, "response": data.captcha},
                    ) as resp:
                        try:
                            resp_data = await resp.json()
                            if not resp_data["success"]:
                                print("CAPTCHA FAILED")
                                return
                        except KeyError:
                            print("CAPTCHA FAILED")
                            return
            except TypeError:
                pass
    # --- END checking captcha ---
    if await redis.get(f"game_session:{data.game_pin}:players:{data.username}") is not None:
        await sio.emit("username_already_exists", room=sid)
        return

    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "sid_custom": sid,
        "admin": False,
    }
    await sio.save_session(sid, session)
    await sio.emit(
        "joined_game",
        {
            **json.loads(game_data.json(exclude={"quiz_id", "questions", "user_id"})),
            "question_count": len(game_data.questions),
            "question_show": game_data.question_show
        },
        room=sid,
    )
    redis_res = await redis.get(f"game_session:{data.game_pin}")
    redis_res = GameSession.parse_raw(redis_res)
    await redis.set(f"game_session:{data.game_pin}:players:{data.username}", sid, ex=7200)
    await redis.sadd(f"game_session:{data.game_pin}:players", GamePlayer(username=data.username, sid=sid).json())
    if data.custom_field == "":
        data.custom_field = None
    if data.custom_field is not None:
        await redis.hset(f"game:{data.game_pin}:players:custom_fields", data.username, data.custom_field)

    # await redis.set(
    #     f"game_session:{data.game_pin}",
    #     GameSession(admin=redis_res.admin, game_id=redis_res.game_id, answers=[]).json(),
    #     ex=18000,
    # )
    await sio.emit(
        "player_joined",
        {"username": data.username, "sid": sid, "question_show": game_data.question_show},
        room=f"admin:{data.game_pin}",
    )
    # +++ Time-Sync +++
    encrypted_datetime = fernet.encrypt(datetime.now().isoformat().encode("utf-8")).decode("utf-8")
    await sio.emit("time_sync", encrypted_datetime, room=sid)
    # --- Time-Sync ---
    await sio.enter_room(sid, data.game_pin)
    # Initialize player score to 0 when they join
    await redis.hset(f"game_session:{data.game_pin}:player_scores", data.username, 0)


@sio.event
async def start_game(sid: str, _data: dict):
    session = await sio.get_session(sid)
    if not session["admin"]:
        return
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    game_data.started = True
    await redis.set(f"game:{session['game_pin']}", game_data.json(), ex=7200)
    await redis.delete(f"game_in_lobby:{game_data.user_id.hex}")
    await sio.emit("start_game", room=session["game_pin"])

    # Automatically set the first question
    await set_question_number(sid, '0')


class _RegisterAsAdminData(BaseModel):
    game_pin: str
    game_id: str


@sio.event
async def register_as_admin(sid: str, data: dict):
    try:
        data = _RegisterAsAdminData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    game_pin = data.game_pin
    game_id = data.game_id
    if (await redis.get(f"game_session:{game_pin}")) is None:
        await redis.set(
            f"game_session:{game_pin}",
            GameSession(admin=sid, game_id=game_id, answers=[]).json(),
            ex=7200,
        )

        await sio.emit(
            "registered_as_admin",
            {"game_id": game_id, "game": await redis.get(f"game:{game_pin}")},
            room=sid,
        )
        async with sio.session(sid) as session:
            session["game_pin"] = game_pin
            session["admin"] = True
            session["remote"] = False
        await sio.enter_room(sid, game_pin)
        await sio.enter_room(sid, f"admin:{data.game_pin}")
    else:
        await sio.emit("already_registered_as_admin", room=sid)


@sio.event
async def get_question_results(sid: str, data: dict):
    session = await sio.get_session(sid)
    if not session["admin"]:
        return

    redis_res = await redis.get(f"game_session:{session['game_pin']}:{data['question_number']}")
    if redis_res is None:
        redis_res = []
    else:
        redis_res = AnswerDataList.parse_raw(redis_res).dict()["__root__"]
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    game_data.question_show = False
    await redis.set(f"game:{session['game_pin']}", game_data.json())
    game_pin = session["game_pin"]

    await sio.emit("question_results", redis_res, room=game_pin)


class ABCDQuizAnswerWithoutSolution(BaseModel):
    answer: str
    color: str | None


class RangeQuizAnswerWithoutSolution(BaseModel):
    min: int
    max: int


class ReturnQuestion(QuizQuestion):
    answers: list[ABCDQuizAnswerWithoutSolution] | RangeQuizAnswerWithoutSolution | list[VotingQuizAnswer]
    type: QuizQuestionType = QuizQuestionType.ABCD

    @validator("answers")
    def answers_not_none_if_abcd_type(cls, v, values):
        if values["type"] == QuizQuestionType.ABCD and type(v[0]) is not ABCDQuizAnswerWithoutSolution:
            raise ValueError("Answers can't be none if type is ABCD")
        if values["type"] == QuizQuestionType.RANGE and type(v) is not RangeQuizAnswerWithoutSolution:
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        # skipcq: PTC-W0047
        if values["type"] == QuizQuestionType.VOTING and type(v[0]) is not VotingQuizAnswer:
            pass
        return v


@sio.event
async def set_question_number(sid, data: str):
    # data is just a number (as a str) of the question
    session = await sio.get_session(sid)
    if not session["admin"]:
        return
    game_pin = session["game_pin"]
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    game_data.current_question = int(float(data))
    game_data.question_show = True
    await redis.set(f"game:{session['game_pin']}", game_data.json(), ex=7200)
    await redis.set(f"game:{session['game_pin']}:current_time", datetime.now().isoformat(), ex=7200)
    temp_return = game_data.dict(include={"questions"})["questions"][int(float(data))]
    if game_data.questions[int(float(data))].type == QuizQuestionType.SLIDE:
        await sio.emit(
            "set_question_number",
            {
                "question_index": int(float(data)),
            },
            room=sid,
        )
        return
    if game_data.questions[int(float(data))].type == QuizQuestionType.VOTING:
        for i in range(len(temp_return["answers"])):
            temp_return["answers"][i] = VotingQuizAnswer(**temp_return["answers"][i])
    temp_return["type"] = game_data.questions[int(float(data))].type
    if temp_return["type"] == QuizQuestionType.ORDER:
        random.shuffle(temp_return["answers"])
    await sio.emit(
        "set_question_number",
        {
            "question_index": int(float(data)),
            "question": ReturnQuestion(**temp_return).dict(),
        },
        room=game_pin,
    )


class _SubmitAnswerDataOrderType(BaseModel):
    answer: str


class _SubmitAnswerData(BaseModel):
    question_index: int
    answer: str
    complex_answer: list[_SubmitAnswerDataOrderType] | None


async def get_unique_player_count(game_pin: str) -> int:
    players = await redis.smembers(f"game_session:{game_pin}:players")
    usernames = set()
    for player_json in players:
        player = GamePlayer.parse_raw(player_json)
        usernames.add(player.username)
    return len(usernames)


@sio.event
async def submit_answer(sid: str, data: dict):
    now = datetime.now()
    try:
        data = _SubmitAnswerData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    # Get the current question start time from Redis
    session = await sio.get_session(sid)
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    time_q_started_str = await redis.get(f"game:{session['game_pin']}:current_time")

    if not time_q_started_str:
        await sio.emit("error", room=sid)
        print("No question start time found")
        return

    time_q_started = datetime.fromisoformat(time_q_started_str)

    # Calculate the elapsed time since the question started
    elapsed_time = (now - time_q_started).total_seconds()

    # Check if the time is already up
    max_time = float(game_data.questions[game_data.current_question].time)
    if elapsed_time > max_time + 1:
        await sio.emit("time_up", room=sid)
        game_data.question_show = False
        return  # The time is up, no more answers are accepted

    answer_right = False
    if game_data.questions[int(float(data.question_index))].type == QuizQuestionType.ABCD:
        for answer in game_data.questions[int(float(data.question_index))].answers:
            if answer.answer == data.answer and answer.right:
                answer_right = True
                break
    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.RANGE:
        if (
            game_data.questions[int(float(data.question_index))].answers.min_correct
            <= int(float(data.answer))
            <= game_data.questions[int(float(data.question_index))].answers.max_correct
        ):
            answer_right = True
    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.VOTING:
        answer_right = False
    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.ORDER:
        if data.complex_answer is None:
            answer_right = False
        else:
            question = game_data.questions[int(float(data.question_index))]
            correct_answers = []
            for a in question.answers:
                correct_answers.append({"answer": a.answer})
            answer_order = []
            for a in data.dict()["complex_answer"]:
                answer_order.append(a["answer"])
            data.answer = ", ".join(answer_order)
            if correct_answers == data.dict()["complex_answer"]:
                answer_right = True

    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.TEXT:
        answer_right = False
        for q in game_data.questions[int(float(data.question_index))].answers:
            if q.case_sensitive:
                if data.answer == q.answer:
                    answer_right = True
                    break
            else:
                if data.answer.lower() == q.answer.lower():
                    answer_right = True
                    break
    elif game_data.questions[int(data.question_index)].type == QuizQuestionType.CHECK:
        correct_string = ""
        for i, a in enumerate(game_data.questions[int(float(data.question_index))].answers):
            if a.right:
                correct_string += str(i)
        answer_right = bool(correct_string == data.answer)
    else:
        raise NotImplementedError
    session = await sio.get_session(sid)
    latency = int(float(session.get("ping", 0)))  # use 0 if ping is not set
    time_q_started = datetime.fromisoformat(await redis.get(f"game:{session['game_pin']}:current_time"))

    diff = (time_q_started - now).total_seconds() * 1000  # - timedelta(milliseconds=latency)
    score = 0
    if answer_right:
        score = calculate_score(
            abs(diff) - latency, int(float(game_data.questions[int(float(data.question_index))].time))
        )
        if score > 1000:
            score = 1000
    await redis.hincrby(f"game_session:{session['game_pin']}:player_scores", session["username"], score)
    answer_data = AnswerData(
        username=session["username"],
        answer=data.answer,
        right=answer_right,
        time_taken=abs(diff) - latency,
        score=score,
    )
    answers = await redis.get(f"game_session:{session['game_pin']}:{data.question_index}")
    answers = await set_answer(
        answers, game_pin=session["game_pin"], data=answer_data, q_index=int(float(data.question_index))
    )
    player_count = await get_unique_player_count(session['game_pin'])
    await sio.emit("player_answer", {})
    if len(answers.__root__) == player_count:
        # await sio.emit(
        #     "question_results",
        #     await redis.get(f"game_session:{session['game_pin']}:{data.question_index}"),
        #     room=session["game_pin"],
        # )
        game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
        game_data.question_show = False
        await redis.set(f"game:{session['game_pin']}", game_data.json())
        await sio.emit("everyone_answered", {})

    await sio.emit("answer_acknowledged", room=sid)

# await redis.set(f"game_data:{session['game_pin']}", json.dumps(data))


@sio.event
async def get_final_results(sid: str, _data: dict):
    session: dict = await sio.get_session(sid)
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    if not session["admin"]:
        return
    results = await generate_final_results(game_data, session["game_pin"])
    await sio.emit("final_results", results, room=session["game_pin"])


@sio.event
async def get_export_token(sid: str):
    session = await sio.get_session(sid)
    if not session["admin"]:
        return
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    results = await generate_final_results(game_data, session["game_pin"])
    token = os.urandom(32).hex()
    await redis.set(f"export_token:{token}", json.dumps(results), ex=7200)
    await sio.emit("export_token", token, room=sid)


@sio.event
async def show_solutions(sid: str, _data: dict):
    session: dict = await sio.get_session(sid)
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    if not session["admin"]:
        return
    # Set question_show to False
    game_data.question_show = False
    # Save the updated game data back to Redis
    await redis.set(f"game:{session['game_pin']}", game_data.json())
    # Emit the solutions to all connected clients
    await sio.emit("solutions", game_data.questions[game_data.current_question].dict(), room=session["game_pin"])


@sio.event
async def echo_time_sync(sid: str, data: str):
    then_dec = fernet.decrypt(data).decode("utf-8")
    then = datetime.fromisoformat(then_dec)
    now = datetime.now()
    delta = now - then
    async with sio.session(sid) as session:
        session["ping"] = delta.microseconds / 1000


class _KickPlayerInput(BaseModel):
    username: str


@sio.event
async def kick_player(sid: str, data: dict):
    try:
        data = _KickPlayerInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session: dict = await sio.get_session(sid)
    if not session["admin"]:
        return

    player_sid = await redis.get(f"game_session:{session['game_pin']}:players:{data.username}")
    await redis.srem(
        f"game_session:{session['game_pin']}:players", GamePlayer(username=data.username, sid=player_sid).json()
    )
    await sio.leave_room(player_sid, session["game_pin"])
    await sio.emit("kick", room=player_sid)
    await sio.emit("disconnect_reason", {"reason": "You were kicked by the admin."}, room=player_sid)


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    reason = "Connection lost."
    if session.get('kicked', False):
        reason = "You were kicked from the game."
    
    await sio.emit("disconnect_reason", {"reason": reason}, room=sid)


class _RegisterAsRemoteInput(BaseModel):
    game_pin: str
    game_id: str


@sio.event
async def register_as_remote(sid: str, data: dict):
    try:
        data = _RegisterAsRemoteInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    await sio.emit(
        "registered_as_admin",
        {"game_id": data.game_id, "game": await redis.get(f"game:{data.game_pin}")},
        room=sid,
    )
    await sio.emit("control_visibility", {"visible": False}, room=f"admin:{data.game_pin}")
    async with sio.session(sid) as session:
        session["game_pin"] = data.game_pin
        session["admin"] = True
        session["remote"] = True
    await sio.enter_room(sid, data.game_pin)
    await sio.enter_room(sid, f"admin:{data.game_pin}")


class _SetControlVisibilityInput(BaseModel):
    visible: bool


@sio.event
async def set_control_visibility(sid: str, data: dict):
    try:
        data = _SetControlVisibilityInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    session: dict = await sio.get_session(sid)
    await sio.emit("control_visibility", {"visible": data.visible}, room=f"admin:{session['game_pin']}")


@sio.event
async def save_quiz(sid: str):
    session: dict = await sio.get_session(sid)
    if not session["admin"]:
        return
    await save_quiz_to_storage(session["game_pin"])
    await sio.emit("results_saved_successfully")
