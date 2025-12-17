from typing import Union, List

from fastapi import HTTPException
from pydantic import UUID4

from auth.schemas.role import RoleOut, SingleRoleOut
from main.utils.logger import log


async def list_roles(
        cls,
        search: str = None,
        id: UUID4 = None,
        user_id: UUID4 = None,
        skip: int = 0,
        limit: int = 100,
) -> List[Union[RoleOut, SingleRoleOut]]:
    log.debug(f'init list role with skip: {skip}, limit: {limit}')

    if id and search: raise HTTPException(
        status_code=400, detail='Search and id are mutually exclusive'
    )

    if id:
        role = await cls.get(id)
        return [role]

    if user_id:
        roles = await cls.get_user_roles(user_id)
        return roles

    results = await cls.repo.list(
        search=search,
        skip=skip,
        limit=limit,
    )
    return await cls.to_domain(results, list=True)
