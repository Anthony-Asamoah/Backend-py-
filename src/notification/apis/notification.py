from typing import List

from fastapi import Depends

from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter
from notification.schemas.notification import NotificationOut
from notification.use_cases.notification import notification_service

notification_router = SafeAPIRouter()

notification_router.post(
    '',
    response_model=NotificationOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['notification.notification:create', 'notification.*:*']))],
    summary="Create and send a notification (testing only)",
)(notification_service.create)

notification_router.get(
    '',
    response_model=List[NotificationOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['notification.notification:read', 'notification.*:*']))],
    summary="List notifications or get by id",
)(notification_service.read)

notification_router.post(
    '/{id}/retry',
    response_model=NotificationOut,
    status_code=200,
    dependencies=[Depends(check_user_permission(['notification.notification:update', 'notification.*:*']))],
    summary="Retry failed notification",
)(notification_service.retry)

notification_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['notification.notification:delete', 'notification.*:*']))],
    summary="Delete notification by ID",
)(notification_service.delete)
