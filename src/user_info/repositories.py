from typing import Optional

from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from main.utils.base_classes import BaseRepository
from main.utils.logger import log
from user_info.models import UserInfo


class UserInfoRepository(BaseRepository):

    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100
    ) -> list[UserInfo]:
        log.debug(f'init list user info with skip: {skip}, limit: {limit}')

        search_fields = ['first_name', 'last_name', 'other_names', 'email', 'phone_number']
        if search:
            query = (
                self.model.objects
                .annotate(search=SearchVector(*search_fields))
                .filter(search=search)
            )
            return await self.paginate_queryset(query, skip, limit)

        query = self.model.objects.all()
        result = await self.paginate_queryset(query, skip, limit)
        return result

    async def get_user_by_email_or_phone_number(
            self,
            email: Optional[str] = None,
            phone_number: Optional[str] = None,
    ) -> Optional[UserInfo]:
        log.debug('init get_user_by_email_or_phone_number')
        if not email and not phone_number: return None

        filters = []
        if email: filters.append(Q(email=email))
        if phone_number: filters.append(Q(phone_number=phone_number))

        if not filters: return None

        # Combine filters with OR logic
        query_filter = filters[0]
        for f in filters[1:]:
            query_filter |= f

        return await self.model.objects.filter(query_filter).afirst()


user_info_repo = UserInfoRepository(UserInfo)
