from fastapi import BackgroundTasks, HTTPException

from auth.schemas.role import RoleCreate, RoleRepoCreate
from main.utils.logger import log


async def create_role(cls, payload: RoleCreate, background_tasks: BackgroundTasks) -> RoleCreate:
    log.debug(f'init new role with payload: {payload}')

    # validate role
    payload.name = payload.name.title()
    existing_role = await cls.repo.get_by_name(payload.name)
    if existing_role: raise HTTPException(
        status_code=400, detail=f'{payload.name} already exists'
    )

    # create role
    new_role = await cls.repo.create(RoleRepoCreate(**payload.model_dump()))

    # add permissions
    await cls.repo.add_permissions(new_role.id, payload.permissions_ids)

    return await cls.to_domain(new_role)
