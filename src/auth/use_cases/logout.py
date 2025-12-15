from auth.utils.blacklist_token import blacklist_token
from main.utils.logger import log


async def logout(cls, access_token: str) -> None:
    log.debug(f'init logout with token: {access_token}')
    await blacklist_token(access_token)
