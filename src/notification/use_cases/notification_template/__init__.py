from typing import Annotated

from auth.schemas.user_account import UserAccountOut, CurrentAccountPayload
from auth.utils import get_current_user
from fastapi import Depends
from main.utils.base_classes import BaseService
from notification.models import NotificationTemplate
from notification.repositories import notification_template_repo
from notification.schemas.notification_template import NotificationTemplateOut, NotificationTemplateCreate, \
    NotificationTemplateUpdate
from pydantic import UUID4

from .create_notification_template import create_notification_template
from .delete_notification_template import delete_notification_template
from .get_notification_template import get_notification_template
from .get_notification_template_by_name import get_notification_template_by_name
from .list_notification_templates import list_notification_templates
from .update_notification_template import update_notification_template


class NotificationTemplateService(BaseService[NotificationTemplate, NotificationTemplateOut]):
    """Methods to handle notification template domain operations."""

    async def create(
            self,
            payload: NotificationTemplateCreate,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Create a new notification template."""
        return await create_notification_template(self, payload)

    async def read(
            self,
            search: str = None,
            id: UUID4 = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of notification templates."""
        if id:
            return [await self.get(id)]
        return await list_notification_templates(self, search, skip, limit)

    async def get(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Get notification template by ID."""
        return await get_notification_template(self, id)

    async def get_by_name(self, name: str):
        """Get notification template by name (internal use)."""
        return await get_notification_template_by_name(self, name)

    async def update(
            self,
            id: UUID4,
            payload: NotificationTemplateUpdate,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Update notification template with partial data."""
        return await update_notification_template(self, id, payload)

    async def delete(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> None:
        """Delete notification template by ID."""
        return await delete_notification_template(self, id)


notification_template_service = NotificationTemplateService(
    repository=notification_template_repo,
    out_schema=NotificationTemplateOut
)