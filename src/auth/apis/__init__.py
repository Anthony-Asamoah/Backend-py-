from auth.apis.permission import permission_router
from auth.apis.role import role_router
from auth.apis.user_account import user_account_router
from main.utils.exception_handling import SafeAPIRouter

auth_router = SafeAPIRouter()

auth_router.include_router(user_account_router, prefix='/accounts', tags=['User Account'])
auth_router.include_router(role_router, prefix='/roles', tags=['Role'])
auth_router.include_router(permission_router, prefix='/permissions', tags=['Permission'])
