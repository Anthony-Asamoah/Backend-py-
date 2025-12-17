from typing import Annotated

from fastapi import Depends, BackgroundTasks
from pydantic import UUID4

from auth.models import Permission
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from .create_permission import create_permission
from .delete_permission import delete_permission
from .get_permission import get_permission
from .list_permissions import list_permissions
from .update_permission import update_permission
from ...repositories.permission_repo import permission_repo
from ...schemas.permission import PermissionOut, PermissionCreate, PermissionUpdate
from ...schemas.user_account import UserAccountOut


class PermissionService(BaseService[Permission, PermissionOut]):
    """Methods to handle permission domain operations."""

    async def create(
            self,
            payload: PermissionCreate,
            tasks: BackgroundTasks = None,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Create a new permission."""
        return await create_permission(self, payload, tasks)

    async def read(
            self, *,
            search: str = None,
            id: UUID4 = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of permissions."""
        return await list_permissions(self, search, id, skip, limit)

    async def update(
            self, *,
            id: UUID4,
            payload: PermissionUpdate,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Get a paginated list of permissions."""
        return await update_permission(self, id, payload)

    async def delete(
            self,
            id: UUID4,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by ID."""
        return await delete_permission(self, id)

    async def get(
            self,
            id: UUID4,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Get permission by ID."""
        return await get_permission(self, id)


permission_service = PermissionService(
    repository=permission_repo,
    out_schema=PermissionOut
)
