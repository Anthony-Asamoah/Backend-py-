from typing import Optional

from auth.models import Permission
from main.utils.base_classes import BaseRepository


class PermissionRepository(BaseRepository):

    async def get_by_name(self, name: str) -> Optional[Permission]:
        return await self.model.objects.filter(name__icontains=name).afirst()


permission_repo = PermissionRepository(
    model=Permission,
    search_fields=['name']
)
