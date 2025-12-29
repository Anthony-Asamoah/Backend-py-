import asyncio

from fastapi import HTTPException, status
from main.utils.logger import log
from notification.schemas.notification import NotificationOut
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus
from pydantic import UUID4

from notification.utils import get_status, get_channels


async def retry_notification(cls, id: UUID4) -> NotificationOut:
    log.debug(f'init retry notification with id: {id}')

    # Import here to avoid circular imports
    from notification.use_cases.notification_dispatch import notification_dispatch_service

    notification = await cls.get(id)

    notification_status = await get_status(notification.dispatches)
    if notification_status != NotificationStatus.FAILED.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Notification already {str(notification_status).lower()}"
        )

    # Get failed dispatches
    notification_channels = await get_channels(notification.dispatches)
    dispatches = await notification_dispatch_service.repo.list(
        notification_id=notification.id,
        user_id=notification.user_info_id,
        channels=[NotificationChannel(channel) for channel in notification_channels] if notification_channels else None,
        status=[NotificationStatus.FAILED]
    )

    # Retry each failed dispatch
    await asyncio.gather(*[
        notification_dispatch_service.retry_dispatch(dispatch_id=dispatch.id)
        for dispatch in dispatches
    ])

    return await cls.get(id)