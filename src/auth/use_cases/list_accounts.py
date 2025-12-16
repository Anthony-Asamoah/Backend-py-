from fastapi import HTTPException

from auth.schema import UserAccountOut
from main.utils.logger import log


async def list_accounts(
        cls,
        search: str = None,
        identifier: str = None,
        is_deleted: bool = None,
        skip: int = 0,
        limit: int = 100,
) -> list[UserAccountOut]:
    log.debug(f'init list user accounts with skip: {skip}, limit: {limit}')

    if identifier and search: raise HTTPException(
        status_code=400, detail='Search and identifier are mutually exclusive'
    )
    if identifier:
        obj = await cls.repo.get_by_identifier(identifier=identifier)
        return [cls.to_domain(obj)]

    results = await cls.repo.list(
        search=search,
        skip=skip,
        limit=limit,
        is_deleted=is_deleted
    )
    return await cls.to_domain(results, list=True)
