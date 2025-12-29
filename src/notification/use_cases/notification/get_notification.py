from fastapi import HTTPException, status
from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification import NotificationOut


async def get_notification(cls, id: UUID4) -> NotificationOut:
    log.debug(f'init get notification with id: {id}')

    notification = await cls.repo.get_by_id(id=id)
    if not notification: raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notification not found"
    )

    return await cls.to_domain(notification)
