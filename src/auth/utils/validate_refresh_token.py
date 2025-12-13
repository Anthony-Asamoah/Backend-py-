from typing import Annotated

from fastapi import Depends, HTTPException
from jose import JWTError, jwt

from auth.schema import UserAccountOut
from main import settings
from main.utils.logger import log


async def validate_refresh_token(token: Annotated[str, Depends(settings.AUTH_SECURITY_SCHEME)]) -> UserAccountOut:
    log.debug(f'init get new access tokens')

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_KEY, algorithms=[settings.ALGORITHM])

        identifier: str = payload.get("sub")
        if identifier is None: raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        log.info(f'identifier {identifier}')
        from auth.use_cases import user_account_service
        user = await user_account_service.get(identifier)
        if user is None: raise credentials_exception

        return user
