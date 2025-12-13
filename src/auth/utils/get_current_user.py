from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from auth.schema import UserAccountOut
from main import settings

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials,
            Depends(settings.AUTH_SECURITY_SCHEME)
        ]
) -> UserAccountOut:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        identifier: str = payload.get("sub")
        if identifier is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    from auth.use_cases import user_account_service
    user = await user_account_service.repo.filter(identifier=identifier).afirst()
    if user is None: raise credentials_exception

    return user
