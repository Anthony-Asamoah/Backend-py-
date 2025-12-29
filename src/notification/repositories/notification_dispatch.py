from datetime import datetime
from typing import List, Optional

from asgiref.sync import sync_to_async
from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from pydantic import UUID4

from main.utils.base_classes import BaseRepository
from main.utils.logger import log
from notification.models import NotificationDispatch
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus


class NotificationDispatchRepository(BaseRepository):

    async def get_by_id(self, id: UUID4) -> Optional[NotificationDispatch]:
        log.debug(f'init get {self.model.__name__} by id: {id}')
        return await self.model.objects.select_related('user').filter(id=id).afirst()

    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
            user_id: UUID4 = None,
            notification_id: UUID4 = None,
            channels: List[NotificationChannel] = None,
            status: List[NotificationStatus] = None,
    ) -> list[NotificationDispatch]:
        log.debug(f'init list notification dispatches with skip: {skip}, limit: {limit}')
        query = self.model.objects.all()

        if date_to:
            query = query.filter(created_on__lte=date_to)
        if date_from:
            query = query.filter(created_on__gte=date_from)
        if user_id:
            query = query.filter(user_id=user_id)
        if notification_id:
            query = query.filter(notification_id=notification_id)
        if channels:
            channel_values = [c.value if hasattr(c, 'value') else c for c in channels]
            query = query.filter(channel__in=channel_values)
        if status:
            status_values = [s.value if hasattr(s, 'value') else s for s in status]
            query = query.filter(status__in=status_values)
        if search:
            results = query.annotate(search=SearchVector(*self.search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        result = await self.paginate_queryset(query, skip, limit)
        return result

    async def mark_as_sent(
            self,
            id: UUID4,
            extra_info=None
    ) -> bool:
        notification = await self.get_by_id(id)
        if not notification:
            return False

        notification.status = NotificationStatus.SENT.value
        notification.sent_on = timezone.now()
        notification.extra_info = extra_info
        notification.error_message = None
        await notification.asave()
        return True

    async def bulk_mark_as_sent(
            self,
            ids: List[UUID4],
            extra_info=None
    ) -> bool:
        if not ids: return False

        sent_on = timezone.now()
        dispatches = await sync_to_async(self.model.objects.filter(id__in=ids))

        if not dispatches: return False

        for dispatch in dispatches:
            dispatch.status = NotificationStatus.SENT.value
            dispatch.sent_on = sent_on
            dispatch.extra_info = extra_info
            dispatch.error_message = None

        await self.model.objects.abulk_update(
            dispatches,
            ['status', 'sent_on', 'extra_info', 'error_message']
        )
        return True

    async def mark_as_delivered(
            self,
            id: UUID4,
            extra_info=None
    ) -> bool:
        notification = await self.get_by_id(id)
        if not notification: return False

        notification.status = NotificationStatus.DELIVERED.value
        notification.extra_info = extra_info
        notification.delivered_on = timezone.now()
        notification.error_message = None
        await notification.asave()
        return True

    async def bulk_mark_as_delivered(
            self,
            ids: List[UUID4],
            extra_info=None
    ) -> bool:
        if not ids: return False

        delivered_on = timezone.now()
        dispatches = await sync_to_async(self.model.objects.filter(id__in=ids))

        if not dispatches: return False

        for dispatch in dispatches:
            dispatch.status = NotificationStatus.DELIVERED.value
            dispatch.extra_info = extra_info
            dispatch.delivered_on = delivered_on
            dispatch.error_message = None

        await self.model.objects.abulk_update(
            dispatches,
            ['status', 'extra_info', 'delivered_on', 'error_message']
        )
        return True

    async def mark_as_read(
            self,
            id: UUID4,
            extra_info=None
    ) -> bool:
        notification = await self.get_by_id(id)
        if not notification: return False

        notification.status = NotificationStatus.READ.value
        notification.extra_info = extra_info
        notification.read_on = timezone.now()
        notification.error_message = None
        await notification.asave()
        return True

    async def bulk_mark_as_read(
            self,
            ids: List[UUID4],
            extra_info=None
    ) -> bool:
        if not ids: return False

        read_on = timezone.now()
        dispatches = await sync_to_async(self.model.objects.filter(id__in=ids))

        if not dispatches: return False

        for dispatch in dispatches:
            dispatch.status = NotificationStatus.READ.value
            dispatch.extra_info = extra_info
            dispatch.read_on = read_on
            dispatch.error_message = None

        await self.model.objects.abulk_update(
            dispatches,
            ['status', 'extra_info', 'read_on', 'error_message']
        )
        return True

    async def mark_as_failed(
            self,
            id: UUID4,
            error_message: str
    ) -> bool:
        notification = await self.get_by_id(id)
        if not notification: return False

        notification.status = NotificationStatus.FAILED.value
        notification.error_message = error_message
        await notification.asave()
        return True

    async def bulk_mark_as_failed(
            self,
            ids: List[UUID4],
            error_message: str
    ) -> bool:
        if not ids: return False

        dispatches = await sync_to_async(self.model.objects.filter(id__in=ids))

        if not dispatches: return False

        for dispatch in dispatches:
            dispatch.status = NotificationStatus.FAILED.value
            dispatch.error_message = error_message

        await self.model.objects.abulk_update(
            dispatches,
            ['status', 'error_message']
        )
        return True


notification_dispatch_repo = NotificationDispatchRepository(
    model=NotificationDispatch,
    search_fields=['subject', 'heading', 'content']
)
