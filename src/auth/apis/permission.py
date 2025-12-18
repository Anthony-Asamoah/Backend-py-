from typing import List

from fastapi import Depends

from auth.schemas.permission import PermissionOut
from auth.use_cases.permission import permission_service
from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter

permission_router = SafeAPIRouter()

permission_router.post(
    '',
    response_model=PermissionOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['auth.permission:create', 'auth.*:*']))],
    summary="Create a new permission",
)(permission_service.create)

permission_router.get(
    '',
    response_model=List[PermissionOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['auth.permission:read', 'auth.*:*']))],
    summary="List all permissions",
)(permission_service.read)

permission_router.patch(
    '/{id}',
    response_model=PermissionOut,
    status_code=200,
    dependencies=[Depends(check_user_permission(['auth.permission:update', 'auth.*:*']))],
    summary="Update a permission",
)(permission_service.update)

permission_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['auth.permission:delete', 'auth.*:*']))],
    summary="Delete a permission by ID",
)(permission_service.delete)
