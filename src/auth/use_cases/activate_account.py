from fastapi import BackgroundTasks, HTTPException

from auth.repositories import revoked_token_repo
from auth.schema import Token
from main.utils.logger import log


async def activate_account(cls, payload: Token, background_tasks: BackgroundTasks) -> None:
    log.debug(f'init new activate account with payload: {payload}')

    token_obj = await revoked_token_repo.get_by_token(payload.token)
    if not token_obj: raise HTTPException(status_code=404)

    await cls.repo.activate_account(token_obj.user_account.id)

    # background_tasks.add_task(function_here)
