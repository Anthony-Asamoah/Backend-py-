from typing import Optional

from main.utils.logger import log
from notification.models import NotificationTemplate


async def get_notification_template_by_name(cls, name: str) -> Optional[NotificationTemplate]:
    log.debug(f'init get notification template by name: {name}')

    notification_template = await cls.repo.get_by_name(name)
    return notification_template