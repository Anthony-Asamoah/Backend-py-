from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoOut


async def list_user_info(
        cls,
        search: str = None,
        id: str = None,
        skip: int = 0,
        limit: int = 100
) -> list[UserInfoOut]:
    log.debug(f'init list users with skip: {skip}, limit: {limit}')

    if id and search: raise HTTPException(
        status_code=400, detail='Search and id are mutually exclusive'
    )

    if id:
        user_info = await cls.get_by_id(id)
        return [user_info]

    result = await cls.repo.list(search, skip, limit)
    return await cls.to_domain(result, list=True)
