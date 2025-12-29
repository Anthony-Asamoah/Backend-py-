from main.utils.logger import log
from notification.channels.base_provider import NotificationProvider, ProviderResponse
from notification.channels.email.main import EmailSender
from notification.models import NotificationDispatch
from user_info.models import UserInfo


class EmailProvider(NotificationProvider):
    """Email notification provider"""

    def __init__(self):
        self.email_service = EmailSender()

    async def send(
            self,
            dispatch: NotificationDispatch,
            user_account: UserInfo,
    ) -> ProviderResponse:
        if not self.email_service: return ProviderResponse(
            success=False,
            response="Email service not configured",
            message='Email service not available'
        )

        try:
            await self.email_service.send_email(
                recipient=user_account.email,
                subject=dispatch.subject or "Notification",
                heading=dispatch.heading,
                content=dispatch.content,
                links=dispatch.links
            )
            return ProviderResponse(
                success=True,
                response=user_account.email,
                message='Email sent successfully'
            )
        except Exception as e:
            log.error(f"Failed to send Email via provider. reason: {str(e)}")
            return ProviderResponse(
                success=False,
                response=str(e),
                message='Failed to send email'
            )


email_provider = EmailProvider()
