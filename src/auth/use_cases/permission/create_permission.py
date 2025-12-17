from fastapi import BackgroundTasks, HTTPException

from auth.schemas.permission import PermissionCreate, PermissionOut, PermissionRepoCreate
from main.utils.logger import log


async def create_permission(cls, payload: PermissionCreate, background_tasks: BackgroundTasks) -> PermissionOut:
    log.debug(f'init new permission with payload: {payload}')

    # validate permission
    payload.name = payload.name.title()
    existing_permission = await cls.repo.get_by_name(payload.name)
    if existing_permission: raise HTTPException(
        status_code=400, detail=f'{payload.name} already exists'
    )

    # create permission
    new_permission = await cls.repo.create(PermissionRepoCreate(**payload.model_dump()))

    return await cls.to_domain(new_permission)
