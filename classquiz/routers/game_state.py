from fastapi import APIRouter, HTTPException
from classquiz.config import redis
from classquiz.db.models import PlayGame

router = APIRouter()


@router.get("/{game_pin}")
async def fetch_game_state(game_pin: str):
    data_redis_res = await redis.get(f"game:{game_pin}")
    if data_redis_res is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")

    data = PlayGame.parse_raw(data_redis_res)

    return {
        "game_pin": data.game_pin,
        "started": data.started,
        "game_mode": data.game_mode,
        "current_question": data.current_question,
        "questions_count": len(data.questions),
        "title": data.title,
        "description": data.description,
        "cover_image": data.cover_image,
        "background_color": data.background_color,
        "background_image": data.background_image,
        "question_show": data.question_show,
        "language_toggle": data.language_toggle
    }
