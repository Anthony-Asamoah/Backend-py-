from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log


async def delete_user_info(self, id: str) -> None:
    log.debug(f'init delete user_info {id}')

    try:
        obj = await self.repo.aget(id=id)
        await obj.adelete()

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
