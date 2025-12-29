import asyncio

from fastapi import HTTPException, BackgroundTasks
from pydantic.v1 import UUID4

from main.utils.logger import log
from notification.schemas.notification import NotificationCreate, NotificationOut, NotificationRepoCreate
from notification.schemas.notification_dispatch import NotificationChannel


async def create_notification(
        cls,
        payload: NotificationCreate,
        user_info_id: UUID4,
        background_tasks: BackgroundTasks = None
) -> NotificationOut:
    log.debug(f'init create notification with payload: {payload}')

    # Import here to avoid circular imports
    from user_info.use_cases import user_info_service
    from notification.use_cases.notification_template import notification_template_service
    from notification.use_cases.notification_dispatch import notification_dispatch_service

    # Get user info
    user_info = await user_info_service.repo.get_by_id(user_info_id)
    if not user_info: raise HTTPException(status_code=404, detail="User info not available")

    # Get template
    template = await notification_template_service.repo.get_by_name(name=payload.template_name)
    if not template: raise HTTPException(status_code=404, detail="Template not found")

    # Create notification
    notification_payload = NotificationRepoCreate(
        template_id=template.cursor,
        user_info_id=user_info.cursor
    )
    notification = await cls.repo.create(notification_payload)
    notification.template = template

    # Determine channels to send
    user_preferred_channels = payload.channels or [
        NotificationChannel.EMAIL,
        NotificationChannel.WEBSOCKET,
        NotificationChannel.SMS,
    ]

    # Create dispatches for each channel
    await asyncio.gather(*[
        notification_dispatch_service.create_dispatch(
            notification=notification,
            channel=channel,
            context=payload.context,
            links=payload.links,
        ) for channel in user_preferred_channels
    ])

    result = await cls.get(notification.id)
    return result
