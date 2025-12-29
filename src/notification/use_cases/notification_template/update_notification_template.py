from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification_template import NotificationTemplateUpdate, NotificationTemplateOut


async def update_notification_template(
        cls,
        id: UUID4,
        payload: NotificationTemplateUpdate
) -> NotificationTemplateOut:
    log.debug(f'init update notification template with id: {id}')

    # Verify template exists
    await cls.get(id)

    notification_template = await cls.repo.update(id=id, payload=payload)
    return await cls.to_domain(notification_template)