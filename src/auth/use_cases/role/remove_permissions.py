from fastapi import BackgroundTasks
from pydantic import UUID4

from main.utils.logger import log


async def remove_permissions(
        cls,
        id: UUID4,
        permissions_ids: list[str],
        background_tasks: BackgroundTasks = None
) -> None:
    log.debug(f'init remove role with {len(permissions_ids)} permissions')

    # get role
    role = await cls.get(id)

    # add permissions
    await cls.repo.remove_permissions(role.id, permissions_ids)
