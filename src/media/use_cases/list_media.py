from fastapi import HTTPException

from main.utils.logger import log
from media.schema import MediaOut


async def list_media(
        cls,
        search: str = None,
        id: str = None,
        skip: int = 0,
        limit: int = 100
) -> list[MediaOut]:
    log.debug(f'init list media with skip: {skip}, limit: {limit}')

    if id and search: raise HTTPException(
        status_code=400, detail='Search and id are mutually exclusive'
    )
    if id:
        media = await cls.get(id)
        return [media]

    result = await cls.repo.list(search, skip, limit)
    return await cls.to_domain(result, list=True)
