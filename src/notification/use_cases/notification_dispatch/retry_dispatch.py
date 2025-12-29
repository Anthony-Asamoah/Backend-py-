from fastapi import HTTPException, status
from pydantic import UUID4

from main.utils.logger import log
from notification.schemas.notification_dispatch import NotificationStatus, NotificationDispatchOut


async def retry_dispatch(cls, dispatch_id: UUID4, silent: bool = False) -> NotificationDispatchOut:
    log.debug(f'init retry_dispatch for dispatch_id: {dispatch_id}')

    dispatch = await cls.repo.get_by_id(dispatch_id)
    if not dispatch:
        if silent: return None
        raise HTTPException(status_code=404, detail="Dispatch not found")

    if dispatch.status != NotificationStatus.FAILED.value:
        if silent: return await cls.to_domain(dispatch)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dispatch already {dispatch.status.lower()}"
        )

    # Retry sending
    await cls.send_dispatch(dispatch_id=dispatch_id)

    # Get updated dispatch
    dispatch = await cls.repo.get_by_id(dispatch_id)
    return await cls.to_domain(dispatch)
