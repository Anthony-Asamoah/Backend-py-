from main.utils.exception_handling import SafeAPIRouter
from notification.apis.notification import notification_router
from notification.apis.notification_dispatch import notification_dispatch_router
from notification.apis.notification_template import notification_template_router

notification_routes = SafeAPIRouter()

notification_routes.include_router(notification_router, prefix='/notifications', tags=['NOTIFICATIONS'])
notification_routes.include_router(
    notification_template_router, prefix='/templates', tags=['NOTIFICATION TEMPLATES']
)
notification_routes.include_router(
    notification_dispatch_router, prefix='/dispatches', tags=['NOTIFICATION DISPATCHES']
)
