from typing import List

from fastapi import Depends

from auth.schemas.user_account import UserAccountOut, UserAccountLoginOut, UserAccountTokens, CurrentAccountOut
from auth.use_cases import user_account_service
from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter

user_account_router = SafeAPIRouter()

# Public endpoints
user_account_router.post(
    '/login',
    response_model=UserAccountLoginOut,
    status_code=200,
    summary="Login with email or phone",
)(user_account_service.login)

user_account_router.post(
    '/logout',
    status_code=204,
    summary="Logout and revoke access token",
)(user_account_service.logout)

user_account_router.post(
    "/refresh",
    response_model=UserAccountTokens,
    status_code=200,
    summary="Refresh access and refresh tokens",
)(user_account_service.refresh)

user_account_router.post(
    "/activate",
    status_code=204,
    summary="Activate user account with token",
)(user_account_service.activate)

user_account_router.post(
    "/change-password",
    status_code=204,
    summary="Change password (requires authentication)",
)(user_account_service.change_password)

user_account_router.post(
    "/reset-password-request",
    status_code=204,
    summary="Request password reset token",
)(user_account_service.reset_password_request)

user_account_router.post(
    "/reset-password",
    status_code=204,
    summary="Reset password with token",
)(user_account_service.reset_password)

# Public registration
user_account_router.post(
    '',
    response_model=UserAccountOut,
    status_code=201,
    summary="Register a new user account",
)(user_account_service.create)

# Current user
user_account_router.get(
    '/current-user',
    response_model=CurrentAccountOut,
    status_code=200,
    summary="Get the current user account (requires authentication)",
)(user_account_service.get_authenticated_user)

# Protected administrative endpoints
user_account_router.get(
    '',
    response_model=List[UserAccountOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['auth.useraccount:read', 'auth.*:*']))],
    summary="List all user accounts (admin only)",
)(user_account_service.read)

user_account_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['auth.useraccount:delete', 'auth.*:*']))],
    summary="Delete a user account by ID (admin only)",
)(user_account_service.delete)

user_account_router.post(
    "/assign-roles",
    status_code=204,
    dependencies=[Depends(check_user_permission(['auth.useraccount:update', 'auth.*:*']))],
    summary="Assign roles to user account (admin only)",
)(user_account_service.assign_roles)

user_account_router.post(
    "/remove-roles",
    status_code=204,
    dependencies=[Depends(check_user_permission(['auth.useraccount:update', 'auth.*:*']))],
    summary="Remove roles from user account (admin only)",
)(user_account_service.remove_roles)
