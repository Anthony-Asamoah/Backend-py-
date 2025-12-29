from typing import List

from fastapi import Depends

from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter
from notification.schemas.notification_template import NotificationTemplateOut
from notification.use_cases.notification_template import notification_template_service

notification_template_router = SafeAPIRouter()

notification_template_router.post(
    '',
    response_model=NotificationTemplateOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['notification.notificationtemplate:create', 'notification.*:*']))],
    summary="Create notification template",
)(notification_template_service.create)

notification_template_router.get(
    '',
    response_model=List[NotificationTemplateOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['notification.notificationtemplate:read', 'notification.*:*']))],
    summary="List notification templates or get by id",
)(notification_template_service.read)

notification_template_router.patch(
    '/{id}',
    response_model=NotificationTemplateOut,
    status_code=200,
    dependencies=[Depends(check_user_permission(['notification.notificationtemplate:update', 'notification.*:*']))],
    summary="Update notification template",
)(notification_template_service.update)

notification_template_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['notification.notificationtemplate:delete', 'notification.*:*']))],
    summary="Delete notification template by ID",
)(notification_template_service.delete)
