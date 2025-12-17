from pydantic import UUID4

from main.utils.logger import log


async def delete_permission(cls, id: UUID4) -> None:
    log.debug(f'init delete permission {id}')

    await cls.get(id)
    await cls.repo.delete(id)
