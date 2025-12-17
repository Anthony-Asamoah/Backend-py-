from typing import List

from fastapi import Depends

from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter
from user_info.schemas import UserInfoOut
from user_info.use_cases import user_info_service

user_info_router = SafeAPIRouter()

user_info_router.post(
    '',
    response_model=UserInfoOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['user_info.create', 'user_info.*']))],
    summary="Create user profile",
)(user_info_service.create)

user_info_router.get(
    '',
    response_model=List[UserInfoOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['user_info.read', 'user_info.*']))],
    summary="List user profiles",
)(user_info_service.read)

user_info_router.patch(
    '/{id}',
    response_model=UserInfoOut,
    status_code=200,
    dependencies=[Depends(check_user_permission(['user_info.update', 'user_info.*']))],
    summary="Update user profile",
)(user_info_service.update)

user_info_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['user_info.delete', 'user_info.*']))],
    summary="Delete user profile by ID",
)(user_info_service.delete)
