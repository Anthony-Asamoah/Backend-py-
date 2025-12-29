from main.utils.logger import log
from notification.channels.base_provider import NotificationProvider, ProviderResponse
from notification.channels.sms.arkesel import ArkeselSmsService
from notification.models import NotificationDispatch
from user_info.models import UserInfo


class SMSProvider(NotificationProvider):
    """SMS notification provider"""

    def __init__(self):
        self.sms_service = ArkeselSmsService()

    async def send(
            self,
            dispatch: NotificationDispatch,
            user_account: UserInfo,
    ) -> ProviderResponse:
        if not self.sms_service: return ProviderResponse(
            success=False,
            response="SMS service not configured",
            message='SMS service not available'
        )

        try:
            result = await self.sms_service.send_sms(
                recipient=user_account.phone_number,
                message=dispatch.content
            )
            return ProviderResponse(
                success=True,
                response=str(result),
                message='SMS sent successfully'
            )
        except Exception as e:
            log.error(f"Failed to send SMS via provider. reason: {str(e)}")
            return ProviderResponse(
                success=False,
                response=str(e),
                message='Failed to send SMS'
            )


sms_provider = SMSProvider()
