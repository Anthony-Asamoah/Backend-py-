from datetime import datetime
from typing import List

from main.utils.logger import log
from notification.schemas.notification_template import NotificationTemplateOut


async def list_notification_templates(
        cls,
        search: str = None,
        skip: int = 0,
        limit: int = 100,
        date_from: datetime = None,
        date_to: datetime = None,
) -> List[NotificationTemplateOut]:
    log.debug(f'init list notification templates with skip: {skip}, limit: {limit}')

    notification_templates = await cls.repo.list(
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    return await cls.to_domain(notification_templates, list=True)