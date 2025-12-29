from main.utils.logger import log
from notification.channels.base_provider import NotificationProvider, ProviderResponse
from notification.models import NotificationDispatch
from user_info.models import UserInfo

try:
    from .ws_service import ws_service
except ImportError:
    log.warning("WebSocket service not available, using stub")
    ws_service = None


class WebSocketProvider(NotificationProvider):
    """WebSocket notification provider"""

    def __init__(self, websocket_service=ws_service):
        self.websocket_service = websocket_service

    async def send(
            self,
            dispatch: NotificationDispatch,
            user_account: UserInfo,
    ) -> ProviderResponse:
        if not self.websocket_service:
            log.info(f"WebSocket service not configured - notification logged: {dispatch.content}")
            return ProviderResponse(
                success=True,
                response=str(user_account.id),
                message='WebSocket notification logged (service not configured)'
            )

        try:
            result = await self.websocket_service.send_notification(
                user_id=dispatch.user_id,
                dispatch=dispatch,
            )
            if not result: raise Exception("User is currently offline")

            return ProviderResponse(
                success=True,
                response=str(result),
                message='WebSocket notification sent successfully'
            )
        except Exception as e:
            log.error(f"Failed to send WebSocket notification. reason: {str(e)}")
            return ProviderResponse(
                success=False,
                response=str(e),
                message='Failed to send WebSocket notification'
            )


websocket_provider = WebSocketProvider()
