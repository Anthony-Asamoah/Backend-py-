from typing import List

from main.utils.exception_handling import SafeAPIRouter
from user_info.schema import UserInfoOut
from user_info.use_cases import user_info_service

user_info_router = SafeAPIRouter()

user_info_router.post(
    '',
    response_model=UserInfoOut,
    status_code=201,
)(user_info_service.create)

user_info_router.get(
    '',
    response_model=List[UserInfoOut],
    status_code=200,
)(user_info_service.read)

user_info_router.patch(
    '/{id}',
    response_model=UserInfoOut,
    status_code=200,
)(user_info_service.update)

user_info_router.delete(
    '/{id}',
    status_code=204,
)(user_info_service.delete)
