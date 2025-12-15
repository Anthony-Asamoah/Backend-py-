from django.utils import timezone

from auth.models import RevokedToken


async def cleanup_expired_revoked_tokens():
    """Prune expired revoked tokens from db"""
    await RevokedToken.objects.annotate().filter(expires_on__lt=timezone.now()).adelete()
