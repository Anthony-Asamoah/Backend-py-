from random import choices
from string import ascii_letters, digits

import pendulum
from django.utils import timezone

from auth.models import PasswordResetToken
from main import settings
from main.utils.base_classes import BaseRepository


class PasswordResetTokenRepository(BaseRepository):
    async def create(self, user_account_cursor: int) -> str:
        obj = PasswordResetToken(
            reset_password_token=''.join(choices(ascii_letters + digits, k=250)),
            expires_on=pendulum.now().add(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
            user_account_id=user_account_cursor,
        )
        await obj.asave()
        return obj.reset_password_token

    async def get_by_token(self, token: str) -> PasswordResetToken:
        result = await (
            self.model.objects
            .select_related('user_account')
            .filter(reset_password_token=token)
            .exclude(expires_on__lte=timezone.now())
            .afirst()
        )
        return result
