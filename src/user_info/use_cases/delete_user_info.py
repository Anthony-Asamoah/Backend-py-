from pydantic import UUID4

from main.utils.logger import log


async def delete_user_info(cls, id: UUID4) -> None:
    log.debug(f'init delete user_info {id}')

    await cls.get(id)
    await cls.repo.delete(id)
