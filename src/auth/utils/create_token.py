from datetime import timedelta
from typing import Optional

import pendulum
from jose import jwt

from main import settings


def create_token(key: str, data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": pendulum.now() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES)
    return create_token(settings.JWT_SECRET_KEY, data, expires_delta)


async def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not expires_delta:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_IN_MINUTES)
    return create_token(settings.JWT_REFRESH_KEY, data, expires_delta)
