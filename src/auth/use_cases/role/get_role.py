from asgiref.sync import sync_to_async
from pydantic import UUID4

from auth.schemas.permission import PermissionOut
from auth.schemas.role import SingleRoleOut
from main.utils.logger import log


async def get_role(cls, id: UUID4) -> SingleRoleOut:
    log.debug(f'init get user role with id: {id}')

    role = await cls.repo.get_by_id(id)
    permissions = await sync_to_async(list)(role.permissions.all())
    result = SingleRoleOut(
        id=role.id,
        name=role.name,
        permissions=[PermissionOut(
            id=p.id,
            name=p.name,
        ) for p in permissions]
    )
    return result
