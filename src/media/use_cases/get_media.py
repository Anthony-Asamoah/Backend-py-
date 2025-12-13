from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log


async def get_media(self, id: str):
    log.debug(f'init get media with id: {id}')

    try:
        obj = await self.repo.aget(id=id)
        return self.to_domain(obj)

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
