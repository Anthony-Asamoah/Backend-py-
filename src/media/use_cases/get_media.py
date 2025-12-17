from fastapi import HTTPException
from pydantic import UUID4

from main.utils.logger import log


async def get_media(cls, id: UUID4):
    log.debug(f'init get media with id: {id}')

    media = await cls.repo.get_by_id(id)
    if not media: raise HTTPException(status_code=404)

    return await cls.to_domain(media)
