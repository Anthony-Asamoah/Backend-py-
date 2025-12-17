from django.utils import timezone

from auth.models import PasswordResetToken, RevokedToken
from main.utils.base_classes import BaseRepository


class RevokedTokenRepository(BaseRepository):
    async def get_by_token(self, token: str) -> PasswordResetToken:
        result = await (
            self.model.objects
            .filter(token=token)
            .exclude(expires_on__lte=timezone.now())
            .afirst()
        )
        return result


revoked_token_repo = RevokedTokenRepository(RevokedToken)
