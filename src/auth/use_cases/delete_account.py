from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log


async def delete_account(self, id: str) -> None:
    log.debug(f'init delete user account {id}')

    try:
        obj = await self.repo.aget(id=id)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
    else:
        obj.is_deleted = True
        obj.asave()
