from fastapi import HTTPException
from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification_template import NotificationTemplateOut


async def get_notification_template(cls, id: UUID4) -> NotificationTemplateOut:
    log.debug(f'init get notification template with id: {id}')

    notification_template = await cls.repo.get_by_id(id=id)
    if not notification_template:
        raise HTTPException(status_code=404, detail="Notification template not found")

    return await cls.to_domain(notification_template)