from pydantic import UUID4

from main.utils.logger import log


async def delete_notification_template(cls, id: UUID4) -> None:
    log.debug(f'init delete notification template with id: {id}')

    # Verify template exists
    await cls.get(id)

    await cls.repo.delete(id=id)