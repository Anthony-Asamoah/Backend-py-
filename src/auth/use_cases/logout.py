import pendulum
from jose import jwt, JWTError

from auth.repositories import revoked_token_repo
from auth.schema import RevokedTokenRepoCreate
from main import settings
from main.utils.logger import log


async def logout(cls, access_token: str) -> None:
    log.debug(f'init logout with token: {access_token}')
    try:
        token_data = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        log.info('Invalid authentication key')
    else:
        await revoked_token_repo.create(RevokedTokenRepoCreate(
            token=access_token,
            expires_on=pendulum.from_timestamp(token_data.get("exp"))
        ))
