from auth.apis.permission import permission_router
from auth.apis.role import role_router
from auth.apis.user_account import user_account_router
from main.utils.exception_handling import SafeAPIRouter

auth_routes = SafeAPIRouter()

auth_routes.include_router(user_account_router, prefix='/accounts', tags=['USER ACCOUNT'])
auth_routes.include_router(role_router, prefix='/roles', tags=['ROLE'])
auth_routes.include_router(permission_router, prefix='/permissions', tags=['PERMISSION'])
