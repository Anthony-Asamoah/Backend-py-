from django.conf import settings

from auth.apis import auth_routes
from main.utils.exception_handling import SafeAPIRouter
from media.api import media_routes
from notification.apis import notification_routes
from user_info.api import user_info_routes

app_router = SafeAPIRouter(prefix=settings.API_PREFIX)


@app_router.get('/health')
async def health():
    return {'status': 'ok'}


app_router.include_router(auth_routes, prefix='/auth')
app_router.include_router(user_info_routes, prefix='/user-info')
app_router.include_router(media_routes, prefix='/media')
app_router.include_router(notification_routes, prefix='/notifications')
