from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoUpdate, UserInfoOut


async def update_user_info(cls, id: str, payload: UserInfoUpdate) -> UserInfoOut:
    log.debug(f'init update user_info id:{id} with payload: {payload}')

    obj = await cls.repo.get_by_id(id=id)
    if not obj: HTTPException(status_code=404)

    result = await cls.repo.update(obj.id, payload)
    return await cls.to_domain(result)
