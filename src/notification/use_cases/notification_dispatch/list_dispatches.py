from datetime import datetime
from typing import List

from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus, NotificationDispatchOut


async def list_dispatches(
        cls,
        skip: int = 0,
        limit: int = 100,
        date_from: datetime = None,
        date_to: datetime = None,
        user_id: UUID4 = None,
        notification_id: UUID4 = None,
        channels: List[NotificationChannel] = None,
        status: List[NotificationStatus] = None,
) -> List[NotificationDispatchOut]:
    log.debug(f'init list dispatches with skip: {skip}, limit: {limit}')

    dispatches = await cls.repo.list(
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        user_id=user_id,
        notification_id=notification_id,
        channels=channels,
        status=status,
    )
    return await cls.to_domain(dispatches, list=True)