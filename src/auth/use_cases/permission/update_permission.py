from fastapi import HTTPException
from pydantic import UUID4

from auth.schemas.permission import PermissionUpdate, PermissionOut
from main.utils.logger import log


async def update_permission(
        cls,
        id: UUID4,
        payload: PermissionUpdate,
) -> PermissionOut:
    log.debug(f'init update permission with payload: {payload}')

    permission = await cls.get(id)

    # validate permission
    if payload.name and payload.name != permission.name:
        payload.name = payload.name.title()
        existing_permission = await cls.repo.get_by_name(payload.name)
        if existing_permission: raise HTTPException(
            status_code=400, detail=f'{payload.name} already exists'
        )

    updated_permission = await cls.repo.update(id, payload)
    return await cls.to_domain(updated_permission)
