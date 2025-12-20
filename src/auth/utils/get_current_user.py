from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from auth.schemas.user_account import CurrentAccountPayload
from auth.utils.authorize_account import authorize_account
from main import settings

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(settings.AUTH_SECURITY_SCHEME)]
) -> CurrentAccountPayload:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        identifier: str = payload.get("sub")
        if identifier is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    # get revoked tokens
    from auth.repositories import revoked_token_repo
    is_revoked = await revoked_token_repo.get_by_token(token)
    if is_revoked: raise credentials_exception

    # retrieve user account
    from auth.use_cases import user_account_service
    account = await user_account_service.repo.get_by_identifier(identifier=identifier)
    is_authorized = await authorize_account(account)
    if not is_authorized: raise credentials_exception

    return CurrentAccountPayload(
        cursor=account.cursor,
        id=account.id,
        identifier=account.identifier,
        identifier_type=account.identifier_type,
        status=account.status,
        is_deleted=account.is_deleted,
        created_on=account.created_on,
    )
