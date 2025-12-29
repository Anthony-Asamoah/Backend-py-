from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification_dispatch import NotificationChannel


async def send_dispatch(cls, dispatch_id: UUID4) -> bool:
    log.info(f'init send_dispatch for dispatch_id: {dispatch_id}')

    dispatch = await cls.repo.get_by_id(dispatch_id)
    if not dispatch:
        log.error(f"Dispatch {dispatch_id} not found")
        return False

    # Get provider for channel
    provider = cls.providers.get(NotificationChannel(dispatch.channel))
    if not provider:
        error_msg = f"Provider not found for {dispatch.channel}"
        log.error(error_msg)
        await cls.repo.mark_as_failed(id=dispatch_id, error_message=error_msg)
        return False

    # Dispatch the notification via provider
    try:
        result = await provider.send(dispatch=dispatch, user_account=dispatch.user)

        # Toggle to the appropriate state
        if result.success:
            await cls.repo.mark_as_sent(id=dispatch_id, extra_info={'provider_response': result.response})
            return True
        else:
            await cls.repo.mark_as_failed(id=dispatch_id, error_message=result.response)
            return False

    except Exception as e:
        log.error(f"Error sending dispatch {dispatch_id}: {str(e)}")
        await cls.repo.mark_as_failed(id=dispatch_id, error_message=str(e))
        return False
