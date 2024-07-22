"""
Session router
"""
import uuid
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import HTMLResponse
from pydantic import BaseModel
from classquiz.utils import validate_session
from classquiz.db.models import User
from classquiz.auth import create_access_token, get_user_from_mail, get_password_hash
from classquiz.config import settings
from datetime import timedelta
import logging

import gzip
import base64

def generate_default_avatar() -> bytes:
    # Placeholder value for avatar
    return base64.b64encode(gzip.compress(b""))

settings = settings()

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

router = APIRouter()

logger = logging.getLogger(__name__)

class SessionRequest(BaseModel):
    """
    Request model for validating a session ID
    """
    session_id: str


class SessionResponse(BaseModel):
    """
    Response model for validating a session ID
    """
    valid: bool
    message: str


@router.post("/validate_session", response_model=SessionResponse)
async def validate_session_endpoint(session_request: SessionRequest):
    """
    Validate a session ID
    """
    try:
        session_data = validate_session(session_request.session_id)
        if not session_data['data']['valid']:
            raise HTTPException(status_code=401, detail="Invalid session")

        return SessionResponse(valid=session_data['data']['valid'], message="Session is valid")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/start_activity")
async def start_activity(request: Request, session_id: str, activity_id: str):
    """
    Start an activity by storing the session ID in local storage and redirecting to
    the activity page
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    # Validate the session
    session_data = validate_session(session_id)
    if not session_data['data']['valid']:
        raise HTTPException(status_code=401, detail=session_data['message'])

    # Get the email from the session data
    email = session_data['data']['content']['email']
    print('email:', email)
    if not email:
        raise HTTPException(status_code=401, detail="Unable to retrieve email from teacher portal")

    # Check if the user exists
    user = await get_user_from_mail(email)
    print(user)
    if not user:
        # Create user on the fly
        user = User(
            email=email,
            username=email,
            password=get_password_hash(uuid.uuid4().hex),
            avatar=generate_default_avatar()
        )
        try:
            await user.save()
            logger.info("User created: %s", user.email)
        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                # Fetch the user again in case it was created in the meantime
                user = await get_user_from_mail(email)
                if not user:
                    logger.error("Failed to create or fetch user: %s", e)
                    raise HTTPException(
                        status_code=500, detail="Error creating or fetching user") from e
            else:
                logger.error("Error creating user: %s", e)
                raise HTTPException(
                    status_code=500, detail="Error creating user") from e

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    # Set access token in HTTPOnly cookie
    response = HTMLResponse(content="")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Redirect to the activity page
    script = f"""
        <script>
            localStorage.setItem('session_id', '{session_id}');
            window.location.href = '/view/{activity_id}';
        </script>
    """
    response = HTMLResponse(content=script)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.headers["Content-Type"] = "text/html"
    return response
