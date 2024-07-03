"""
Utilities for the classquiz package
"""
import json
import requests
from classquiz.config import settings


def validate_session(session_id: str) -> dict:
    """
    Validate a session
    """
    url = settings().validate_session_url

    payload = json.dumps({
        "sessionId": session_id
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings().validate_session_token}'
    }

    if url is not None:
        response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    else:
        raise ValueError('URL is None')

    if response.status_code != 200:
        raise ValueError('Failed to validate session')
    session_data = response.json()

    # Check for the role
    if session_data['data']['content']['role'] != 'teacher':
        session_data['data']['valid'] = False
        session_data['message'] = 'Invalid role'
    else:
        session_data['message'] = 'Session is valid'

    return session_data
