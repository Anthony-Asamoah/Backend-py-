import logging

from auth.schemas.user_account import RefreshToken, UserAccountTokens
from auth.utils import validate_refresh_token, create_access_token, create_refresh_token


async def get_new_access_tokens(cls, payload: RefreshToken) -> UserAccountTokens:
    logging.info(f'init get new access tokens')

    user = await validate_refresh_token(payload.token)
    return UserAccountTokens(
        access_token=await create_access_token(data={"sub": user.identifier}),
        refresh_token=await create_refresh_token(data={"sub": user.identifier}),
    )
