from fastapi import HTTPException
from pydantic import UUID4

from auth.schemas.permission import PermissionOut
from main.utils.logger import log


async def list_permissions(
        cls,
        search: str = None,
        id: UUID4 = None,
        skip: int = 0,
        limit: int = 100,
) -> list[PermissionOut]:
    log.debug(f'init list permission with skip: {skip}, limit: {limit}')

    if id and search: raise HTTPException(
        status_code=400, detail='Search and id are mutually exclusive'
    )
    if id:
        permission = await cls.get(id)
        return [permission]

    results = await cls.repo.list(
        search=search,
        skip=skip,
        limit=limit,
    )
    return await cls.to_domain(results, list=True)
