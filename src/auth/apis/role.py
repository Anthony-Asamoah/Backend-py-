from typing import List, Union

from fastapi import Depends

from auth.schemas.role import RoleOut, SingleRoleOut
from auth.use_cases.role import role_service
from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter

role_router = SafeAPIRouter()

role_router.post(
    '/add-permissions',
    status_code=204,
    dependencies=[Depends(check_user_permission(['role.update', 'role.*']))],
    summary="Add permissions to a role",
)(role_service.add_permissions)

role_router.delete(
    '/remove-permissions',
    status_code=204,
    dependencies=[Depends(check_user_permission(['role.update', 'role.*']))],
    summary="Remove permissions from a role",
)(role_service.remove_permissions)

role_router.post(
    '',
    response_model=RoleOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['role.create', 'role.*']))],
    summary="Create a new role",
)(role_service.create)

role_router.get(
    '',
    response_model=List[Union[RoleOut, SingleRoleOut]],
    status_code=200,
    dependencies=[Depends(check_user_permission(['role.read', 'role.*']))],
    summary="List all roles or get user roles",
)(role_service.read)

role_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['role.delete', 'role.*']))],
    summary="Delete a role by ID",
)(role_service.delete)
