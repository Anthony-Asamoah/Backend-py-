import pendulum
from fastapi import HTTPException
from jose import jwt, JWTError

from auth.models import RevokedToken
from main import settings
from main.utils.logger import log


async def blacklist_token(token: str):
    """create a new revoked token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        log.info('Cannot blacklist an invalid token')
        raise HTTPException(status_code=400, detail="Invalid token")
    else:
        expires_on = pendulum.from_timestamp(payload.get("exp"))
        await RevokedToken.objects.acreate(token=token, expires_on=expires_on)
