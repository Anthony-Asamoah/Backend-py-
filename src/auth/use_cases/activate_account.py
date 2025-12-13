from django.core.exceptions import ObjectDoesNotExist
from fastapi import BackgroundTasks, HTTPException

from auth.schema import Token, UserAccountStatusChoices
from main.utils.logger import log


async def activate_account(cls, payload: Token, background_tasks: BackgroundTasks) -> None:
    log.debug(f'init new activate account with payload: {payload}')
    try:
        account = await cls.repo.aget(id=payload.token)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
    else:
        # todo: implement password reset token
        # background_tasks.add_task(function_here)
        await account.aupdate({'status': UserAccountStatusChoices.ACTIVE})
