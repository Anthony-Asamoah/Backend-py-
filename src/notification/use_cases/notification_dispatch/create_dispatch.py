from typing import Optional, Dict, Any, List

from main.utils.logger import log
from notification.models import Notification
from notification.schemas.notification_dispatch import NotificationChannel, NotificationDispatchOut, \
    NotificationDispatchRepoCreate, DispatchLinkSchema


async def create_dispatch(
        cls,
        notification: Notification,
        channel: NotificationChannel,
        context: Optional[Dict[str, Any]] = None,
        links: Optional[List[DispatchLinkSchema]] = None,
) -> NotificationDispatchOut:
    log.info(f'init create_dispatch for notification: {notification.id}, channel: {channel}')

    template = notification.template

    payload = {
        "notification_id": notification.cursor,
        "user_id": notification.user_info_id,
        "channel": channel.value if hasattr(channel, 'value') else channel,
    }

    # Get the right content for channel
    match channel:
        case NotificationChannel.SMS:
            payload["content"] = cls._replace_variables(template.short_content, context or {})

        case NotificationChannel.WEBSOCKET:
            payload["subject"] = cls._replace_variables(template.subject, context or {})
            payload["heading"] = cls._replace_variables(template.heading, context or {})
            payload["content"] = cls._replace_variables(template.short_content, context or {})
            payload["links"] = [link.model_dump() for link in links] if links else None

        case NotificationChannel.EMAIL:
            payload["subject"] = cls._replace_variables(template.subject, context or {})
            payload["heading"] = cls._replace_variables(template.heading, context or {})
            payload["content"] = cls._replace_variables(template.email_content, context or {})
            payload["links"] = [link.model_dump() for link in links] if links else None

        case _:
            raise Exception(f"Channel {channel} templating not implemented.")

    dispatch = await cls.repo.create(NotificationDispatchRepoCreate(**payload))

    # Send dispatch asynchronously
    await cls.send_dispatch(dispatch_id=dispatch.id)

    return await cls.to_domain(dispatch)
