from datetime import datetime
from typing import Annotated, List, Optional, Dict, Any

from fastapi import Depends
from fastapi.params import Query
from jinja2 import Template, TemplateSyntaxError, UndefinedError
from pydantic import UUID4

from auth.schemas.user_account import CurrentAccountPayload
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from main.utils.logger import log
from notification.channels.email import email_provider
from notification.channels.sms import sms_provider
from notification.channels.websocket import websocket_provider
from notification.models import NotificationDispatch, Notification
from notification.repositories import notification_dispatch_repo
from notification.schemas.notification_dispatch import (
    NotificationDispatchOut,
    NotificationChannel,
    NotificationStatus,
    DispatchLinkSchema
)
from .create_dispatch import create_dispatch
from .list_dispatches import list_dispatches
from .mark_dispatches import (
    mark_as_sent,
    bulk_mark_as_sent,
    mark_as_delivered,
    bulk_mark_as_delivered,
    mark_as_read,
    bulk_mark_as_read,
    mark_as_failed,
    bulk_mark_as_failed
)
from .retry_dispatch import retry_dispatch
from .send_dispatch import send_dispatch


class NotificationDispatchService(BaseService[NotificationDispatch, NotificationDispatchOut]):
    """Methods to handle notification dispatch domain operations."""

    def __init__(self, repository, out_schema):
        super().__init__(repository, out_schema)
        self.providers = {
            NotificationChannel.SMS: sms_provider,
            NotificationChannel.EMAIL: email_provider,
            NotificationChannel.WEBSOCKET: websocket_provider
        }

    async def create_dispatch(
            self,
            notification: Notification,
            channel: NotificationChannel,
            context: Optional[Dict[str, Any]] = None,
            links: Optional[List[DispatchLinkSchema]] = None,
    ):
        """Create and send a notification dispatch."""
        return await create_dispatch(self, notification, channel, context, links)

    async def send_dispatch(self, dispatch_id: UUID4) -> bool:
        """Send a dispatch through its configured provider."""
        return await send_dispatch(self, dispatch_id)

    async def read(
            self,
            id: UUID4 = None,
            skip: int = 0,
            limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
            user_id: UUID4 = None,
            notification_id: UUID4 = None,
            channels: List[NotificationChannel] = Query(None),
            status: List[NotificationStatus] = Query(None),
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of dispatches."""
        if id:
            dispatch = await self.repo.get_by_id(id)
            return [await self.to_domain(dispatch)] if dispatch else []
        return await list_dispatches(
            self, skip, limit, date_from, date_to, user_id, notification_id, channels, status
        )

    async def retry_dispatch(self, dispatch_id: UUID4, silent: bool = False):
        """Retry sending a failed dispatch."""
        return await retry_dispatch(self, dispatch_id, silent)

    # Mark as methods
    async def mark_as_sent(self, id: UUID4, extra_info=None) -> bool:
        """Mark a dispatch as sent."""
        return await mark_as_sent(self, id, extra_info)

    async def bulk_mark_as_sent(self, ids: List[UUID4], extra_info=None) -> bool:
        """Mark multiple dispatches as sent."""
        return await bulk_mark_as_sent(self, ids, extra_info)

    async def mark_as_delivered(self, id: UUID4, extra_info=None) -> bool:
        """Mark a dispatch as delivered."""
        return await mark_as_delivered(self, id, extra_info)

    async def bulk_mark_as_delivered(self, ids: List[UUID4], extra_info=None) -> bool:
        """Mark multiple dispatches as delivered."""
        return await bulk_mark_as_delivered(self, ids, extra_info)

    async def mark_as_read(self, id: UUID4, extra_info=None) -> bool:
        """Mark a dispatch as read."""
        return await mark_as_read(self, id, extra_info)

    async def bulk_mark_as_read(self, ids: List[UUID4], extra_info=None) -> bool:
        """Mark multiple dispatches as read."""
        return await bulk_mark_as_read(self, ids, extra_info)

    async def mark_as_failed(self, id: UUID4, error_message: str) -> bool:
        """Mark a dispatch as failed."""
        return await mark_as_failed(self, id, error_message)

    async def bulk_mark_as_failed(self, ids: List[UUID4], error_message: str) -> bool:
        """Mark multiple dispatches as failed."""
        return await bulk_mark_as_failed(self, ids, error_message)

    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace variables in text using Jinja2 template syntax ({{variable_name}})."""
        if not text:
            return text
        try:
            template = Template(text)
            return template.render(**variables)
        except UndefinedError as e:
            log.warning(f"Missing variable in template: {str(e)}")
            return text
        except TemplateSyntaxError as e:
            log.error(f"Template syntax error: {str(e)}")
            return text
        except Exception as e:
            log.error(f"Error replacing variables: {str(e)}")
            return text


notification_dispatch_service = NotificationDispatchService(
    repository=notification_dispatch_repo,
    out_schema=NotificationDispatchOut
)
