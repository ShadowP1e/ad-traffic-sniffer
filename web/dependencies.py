from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from config import config

api_key_cookie = APIKeyCookie(name=config.API_KEY_COOKIE_NAME)


def verify_cookie_token(session_token: str = Depends(api_key_cookie)):
    if session_token != config.API_KEY_COOKIE_VALUE:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Unauthorized",
            headers={"Location": "/login"}
        )
