from datetime import datetime
from typing import Optional

from django.contrib.postgres.search import SearchVector

from main.utils.base_classes import BaseRepository
from main.utils.logger import log
from notification.models import NotificationTemplate


class NotificationTemplateRepository(BaseRepository):
    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> list[NotificationTemplate]:
        log.debug(f'init list user info with skip: {skip}, limit: {limit}')
        query = self.model.objects.all()

        if date_to: query = query.filter(created_on__lte=date_to)
        if date_from: query = query.filter(created_on__gte=date_from)
        if search:
            results = query.annotate(search=SearchVector(*self.search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        result = await self.paginate_queryset(query, skip, limit)
        return result

    async def get_by_name(self, name: str) -> Optional[NotificationTemplate]:
        return await self.model.objects.filter(name__iexact=name).afirst()


notification_template_repo = NotificationTemplateRepository(
    model=NotificationTemplate,
    search_fields=['name', 'subject', 'heading']
)
