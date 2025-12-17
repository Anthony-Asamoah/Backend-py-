from django.conf import settings

from auth.apis import auth_router
from auth.apis.user_account import user_account_router
from main.utils.exception_handling import SafeAPIRouter
from user_info.api import user_info_router
from media.api import media_router

app_router = SafeAPIRouter(prefix=settings.API_PREFIX)


@app_router.get('/health')
async def health():
    return {'status': 'ok'}


app_router.include_router(auth_router, prefix='/auth')
app_router.include_router(user_info_router, prefix='/user-info', tags=['USER PROFILES'])
app_router.include_router(media_router, prefix='/media', tags=['MEDIA'])
