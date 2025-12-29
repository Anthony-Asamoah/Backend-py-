from datetime import datetime
from typing import List, Optional

from django.contrib.postgres.search import SearchVector
from pydantic import UUID4

from main.utils.base_classes import BaseRepository
from main.utils.logger import log
from notification.models import Notification
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus


class NotificationRepository(BaseRepository):

    async def get_by_id(self, id: UUID4) -> Optional[Notification]:
        log.debug(f'init get notification by id: {id}')
        return await (
            self.model.objects
            .select_related('user_info')
            .prefetch_related('dispatches')
            .filter(id=id)
            .afirst()
        )

    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
            user_id: UUID4 = None,
            channel: NotificationChannel = None,
            status: List[NotificationStatus] = None,
    ) -> list[Notification]:
        log.debug(f'init list notifications with skip: {skip}, limit: {limit}')
        query = self.model.objects.all()

        if date_to: query = query.filter(created_on__lte=date_to)
        if date_from: query = query.filter(created_on__gte=date_from)
        if user_id: query = query.filter(user_id=user_id)
        if status: 
            # Filter by dispatch status using related field
            status_values = [s.value if hasattr(s, 'value') else s for s in status]
            query = query.filter(dispatches__status__in=status_values).distinct()
        if channel: 
            # Filter by dispatch channel using related field
            channel_value = channel.value if hasattr(channel, 'value') else channel
            query = query.filter(dispatches__channel=channel_value).distinct()
        if search:
            results = query.annotate(search=SearchVector(*self.search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        result = await self.paginate_queryset(query, skip, limit)
        return result


notification_repo = NotificationRepository(
    model=Notification,
    search_fields=[
        'template__name', 'template__subject', 'template__heading',
        'user__first_name', 'user__last_name', 'user__email', 'user__phone_number'
    ]
)