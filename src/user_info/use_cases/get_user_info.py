from typing import Optional

from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoOut


async def get_user_info(self, id: str) -> Optional[UserInfoOut]:
    log.debug(f'init get user_info with id: {id}')

    obj = await self.repo.get_by_id(id=id)
    if not obj: raise HTTPException(status_code=404)
    return await self.to_domain(obj)
