from typing import Optional, List

from asgiref.sync import sync_to_async
from pydantic import UUID4

from auth.models import Role, Permission
from main.utils.base_classes import BaseRepository, ModelType
from main.utils.logger import log


class RoleRepository(BaseRepository):

    async def add_permissions(self, role_id: UUID4, permissions_ids: list[str]) -> None:
        """Add permissions to a role."""
        log.debug(f'Adding {len(permissions_ids)}  permissions to role {role_id}')

        if not permissions_ids: return

        role = await self.get_by_id(role_id)
        if not role: raise ValueError(
            f"Role with id {role_id} not found"
        )

        # Get permission objects by IDs
        permissions = await sync_to_async(list)(
            Permission.objects.filter(id__in=permissions_ids)
        )

        if not permissions: raise ValueError(
            f"No valid permissions found with provided IDs"
        )

        # Add permissions to role using sync_to_async since ManyToMany operations aren't async yet
        await sync_to_async(role.permissions.add)(*permissions)

    async def remove_permissions(self, role_id: UUID4, permissions_ids: list[str]) -> None:
        """Remove permissions from a role."""
        log.debug(f'Removing permissions {permissions_ids} from role {role_id}')

        if not permissions_ids: return

        role = await self.get_by_id(role_id)
        if not role: raise ValueError(
            f"Role with id {role_id} not found"
        )

        # Get permission objects by IDs
        permissions = await sync_to_async(list)(
            Permission.objects.filter(id__in=permissions_ids)
        )

        if not permissions: raise ValueError(
            f"No valid permissions found with provided IDs"
        )

        # Remove permissions from role using sync_to_async
        await sync_to_async(role.permissions.remove)(*permissions)

    async def get_by_name(self, name: str) -> Optional[Role]:
        return await self.model.objects.filter(name__icontains=name).afirst()

    async def get_by_id(self, id: UUID4) -> Optional[ModelType]:
        return await self.model.objects.prefetch_related('permissions').filter(id=id).afirst()

    async def list_user_roles(self, user_id: UUID4) -> List[ModelType]:
        return await sync_to_async(list)(self.model.objects.prefetch_related('permissions').filter(users__id=user_id))


role_repo = RoleRepository(
    model=Role,
    search_fields=['name']
)
