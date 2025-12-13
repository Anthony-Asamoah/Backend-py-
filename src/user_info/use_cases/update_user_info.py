from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoUpdate


async def update_user_info(cls, id: str, payload: UserInfoUpdate):
    log.debug(f'init update user_info id:{id} with payload: {payload}')

    try:
        obj = await cls.repo.aget(id=id)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)

    obj = await obj.aupdate(payload)
    return cls.to_domain(obj)
