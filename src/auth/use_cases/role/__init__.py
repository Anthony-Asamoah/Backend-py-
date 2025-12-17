from typing import Annotated, List

from fastapi import Depends, BackgroundTasks
from pydantic import UUID4

from auth.models import Role
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from .add_permissions import add_permissions
from .create_role import create_role
from .delete_role import delete_role
from .get_role import get_role
from .get_user_roles import get_user_roles
from .list_roles import list_roles
from .remove_permissions import remove_permissions
from ...repositories.role_repo import role_repo
from ...schemas.role import RoleOut, RoleCreate, SingleRoleOut
from ...schemas.user_account import UserAccountOut


class RoleService(BaseService[Role, RoleOut]):
    """Methods to handle role domain operations."""

    async def add_permissions(
            self,
            role_id: UUID4,
            permissions_ids: list[str],
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Add permissions to role."""
        return await add_permissions(self, role_id, permissions_ids)

    async def remove_permissions(
            self,
            role_id: UUID4,
            permissions_ids: list[str],
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Remove permissions from role."""
        return await remove_permissions(self, role_id, permissions_ids)

    async def create(
            self,
            payload: RoleCreate,
            tasks: BackgroundTasks = None,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Create a new role."""
        return await create_role(self, payload, tasks)

    async def read(
            self, *,
            search: str = None,
            id: UUID4 = None,
            user_id: UUID4 = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of roles."""
        return await list_roles(self, search, id, user_id, skip, limit)

    async def delete(
            self,
            id: UUID4,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by ID."""
        return await delete_role(self, id)

    async def get(
            self,
            id: UUID4,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> SingleRoleOut:
        """Get role by ID."""
        return await get_role(self, id)

    async def get_user_roles(
            self,
            user_id: UUID4,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> List[SingleRoleOut]:
        """Get all roles for a user"""
        return await get_user_roles(self, user_id)


role_service = RoleService(
    repository=role_repo,
    out_schema=RoleOut
)
