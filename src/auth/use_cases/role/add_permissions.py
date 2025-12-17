from pydantic import UUID4

from main.utils.logger import log


async def add_permissions(cls, id: UUID4, permissions_ids: list[str]) -> None:
    log.debug(f'init new role with {len(permissions_ids)} permissions')

    # get role
    role = await cls.get(id)

    # add permissions
    await cls.repo.add_permissions(role.id, permissions_ids)
