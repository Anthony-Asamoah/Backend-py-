from typing import List

from auth.schema import UserAccountOut, UserAccountLoginOut, UserAccountTokens
from auth.use_cases import user_account_service
from main.utils.exception_handling import SafeAPIRouter

user_account_router = SafeAPIRouter()

user_account_router.post(
    '/login',
    response_model=UserAccountLoginOut,
    status_code=200,
)(user_account_service.login)

user_account_router.post(
    "/refresh",
    response_model=UserAccountTokens,
    status_code=200,
)(user_account_service.refresh)

user_account_router.post(
    "/activate",
    status_code=204,
)(user_account_service.activate)

user_account_router.post(
    "/change-password",
    status_code=204,
)(user_account_service.change_password)

user_account_router.post(
    '',
    response_model=UserAccountOut,
    status_code=201,
)(user_account_service.create)

user_account_router.get(
    '',
    response_model=List[UserAccountOut],
    status_code=200,
)(user_account_service.read)

user_account_router.delete(
    '/{id}',
    status_code=204,
)(user_account_service.delete)
