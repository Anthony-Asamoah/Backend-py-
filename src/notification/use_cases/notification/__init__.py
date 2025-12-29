from datetime import datetime
from typing import Annotated, List

from fastapi import Depends, BackgroundTasks
from fastapi.params import Query
from pydantic import UUID4, BaseModel

from auth.schemas.user_account import CurrentAccountPayload
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from notification.models import Notification
from notification.repositories import notification_repo
from notification.schemas.notification import NotificationOut, NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus, NotificationDispatchOut
from user_info.schemas import UserInfoOut
from .create_notification import create_notification
from .delete_notification import delete_notification
from .get_notification import get_notification
from .list_notifications import list_notifications
from .retry_notification import retry_notification


class NotificationService(BaseService[Notification, NotificationOut]):
    """Methods to handle notification domain operations."""

    async def _serialize(self, single_obj: BaseModel):
        result = dict(
            id=single_obj.id,
            template_id=single_obj.template_id,
            user_info_id=single_obj.user_info_id,
            status=await single_obj.status,
            channels=await single_obj.channels,
            elapsed_time=single_obj.elapsed_time,
            dispatches=[NotificationDispatchOut.model_validate(_) async for _ in single_obj.dispatches.all()],
            user_info=UserInfoOut.model_validate(single_obj.user_info)
        )
        return result

    async def create(
            self,
            payload: NotificationCreate,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
            background_tasks: BackgroundTasks = None,
    ):
        """Create a new notification and send it through configured channels."""
        return await create_notification(self, payload, current_user.id, background_tasks)

    async def read(
            self,
            search: str = None,
            id: UUID4 = None,
            skip: int = 0,
            limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
            user_id: UUID4 = None,
            channel: NotificationChannel = None,
            status: List[NotificationStatus] = Query(None),
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of notifications."""
        if id:
            return [await self.get(id)]
        return await list_notifications(self, skip, limit, date_from, date_to, user_id, channel, status)

    async def get(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Get notification by ID."""
        return await get_notification(self, id)

    async def delete(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> None:
        """Delete notification by ID."""
        return await delete_notification(self, id)

    async def retry(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Retry sending a failed notification."""
        return await retry_notification(self, id)


notification_service = NotificationService(
    repository=notification_repo,
    out_schema=NotificationOut
)
