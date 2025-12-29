from main.utils.logger import log
from notification.schemas.notification_template import NotificationTemplateCreate, NotificationTemplateOut


async def create_notification_template(cls, payload: NotificationTemplateCreate) -> NotificationTemplateOut:
    log.debug(f'init create notification_template with payload: {payload}')

    # Normalize template name
    payload.name = payload.name.strip().upper().replace(' ', '-')

    notification_template = await cls.repo.create(payload)
    return await cls.to_domain(notification_template)