from typing import Optional

from django.db.models import Q

from main.utils.base_classes import BaseRepository
from main.utils.logger import log
from user_info.models import UserInfo


class UserInfoRepository(BaseRepository):

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


user_info_repo = UserInfoRepository(
    model=UserInfo,
    search_fields=['first_name', 'last_name', 'other_names', 'email', 'phone_number']
)
