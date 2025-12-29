from datetime import datetime
from typing import List

from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification import NotificationOut
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus


async def list_notifications(
        cls,
        skip: int = 0,
        limit: int = 100,
        date_from: datetime = None,
        date_to: datetime = None,
        user_id: UUID4 = None,
        channel: NotificationChannel = None,
        status: List[NotificationStatus] = None,
) -> List[NotificationOut]:
    log.debug(f'init list notifications with skip: {skip}, limit: {limit}')

    notifications = await cls.repo.list(
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        user_id=user_id,
        channel=channel,
        status=status,
    )
    return await cls.to_domain(notifications, list=True)