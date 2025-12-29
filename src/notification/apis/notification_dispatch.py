from typing import List

from fastapi import Depends

from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter
from notification.schemas.notification_dispatch import NotificationDispatchOut
from notification.use_cases.notification_dispatch import notification_dispatch_service

notification_dispatch_router = SafeAPIRouter()

notification_dispatch_router.get(
    '',
    response_model=List[NotificationDispatchOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['notification.notificationdispatch:read', 'notification.*:*']))],
    summary="List notification dispatches",
)(notification_dispatch_service.read)
