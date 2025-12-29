from pydantic import UUID4

from main.utils.logger import log


async def delete_notification(cls, id: UUID4) -> None:
    log.debug(f'init delete notification with id: {id}')

    # Verify notification exists
    await cls.get(id)

    await cls.repo.delete(id=id)