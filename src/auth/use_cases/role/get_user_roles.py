from typing import List

from asgiref.sync import sync_to_async
from pydantic import UUID4

from auth.schemas.permission import PermissionOut
from auth.schemas.role import SingleRoleOut
from main.utils.logger import log


async def get_user_roles(cls, user_id: UUID4) -> List[SingleRoleOut]:
    """Get all roles assigned to a user with their permissions."""
    log.debug(f'init get user roles with user_id: {user_id}')

    # Verify user exists
    from auth.repositories import user_account_repo
    user = await user_account_repo.get_by_id(user_id)
    if not user: return []

    # Get user's roles with permissions (already prefetched in repo)
    roles = await cls.repo.list_user_roles(user_id)

    # Transform to output schemaw
    result = []
    for role in roles:
        permissions = await sync_to_async(list)(role.permissions.all())
        result.append(SingleRoleOut(
            id=role.id,
            name=role.name,
            permissions=[PermissionOut(
                id=p.id,
                name=p.name,
            ) for p in permissions]
        ))

    return result
