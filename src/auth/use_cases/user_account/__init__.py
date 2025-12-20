from typing import Annotated, List

from fastapi import Depends, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from auth.models import UserAccount
from auth.schemas.password_reset_token import ChangePassword, ResetPassword
from auth.schemas.user_account import (
    UserAccountOut,
    UserAccountLogin,
    RefreshToken,
    UserAccountCreate,
    Token,
    CurrentAccountOut,
    CurrentAccountPayload
)
from auth.utils import get_current_user
from main import settings
from main.utils.base_classes import BaseService
from .activate_account import activate_account
from .change_password import change_password
from .create_account import create_account
from .delete_account import delete_account
from .get_account import get_account
from .get_authenticated_user import get_authenticated_user
from .list_accounts import list_accounts
from .login import login
from .logout import logout
from .refresh_token import get_new_access_tokens
from .reset_password import reset_password
from .reset_password_request import reset_password_request
from ...repositories import user_account_repo


class UserAccountService(BaseService[UserAccount, UserAccountOut]):
    """Methods to handle user account domain operations."""

    async def login(self, payload: UserAccountLogin):
        """Authenticate an account."""
        return await login(self, payload)

    async def logout(self, credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(settings.AUTH_SECURITY_SCHEME)
    ]):
        """Expire a session."""
        return await logout(self, credentials.credentials)

    async def refresh(self, payload: RefreshToken):
        """Refresh a set of tokens."""
        return await get_new_access_tokens(self, payload)

    async def create(self, payload: UserAccountCreate, tasks: BackgroundTasks):
        """Create/register a new account."""
        return await create_account(self, payload, tasks)

    async def activate(
            self,
            payload: Token,
            tasks: BackgroundTasks,
    ) -> None:
        """activate an account."""
        await activate_account(self, payload, tasks)

    async def change_password(
            self, *,
            payload: ChangePassword,
            tasks: BackgroundTasks,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> None:
        """change account password."""
        await change_password(self, current_user.id, payload, tasks)

    async def reset_password_request(
            self, *,
            identifier: str,
            tasks: BackgroundTasks,
    ) -> None:
        """activate an account."""
        await reset_password_request(self, identifier, tasks)

    async def reset_password(
            self, *,
            payload: ResetPassword,
            tasks: BackgroundTasks,
    ) -> None:
        """activate an account."""
        await reset_password(self, payload, tasks)

    async def assign_roles(self, id: UUID4, role_ids: List[UUID4]) -> None:
        return await user_account_repo.assign_roles(id, role_ids)

    async def remove_roles(self, id: UUID4, role_ids: List[UUID4]) -> None:
        return await user_account_repo.remove_roles(id, role_ids)

    async def read(
            self, *,
            search: str = None,
            identifier: str = None,
            is_deleted: bool = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of user accounts."""
        return await list_accounts(self, search, identifier, is_deleted, skip, limit)

    async def delete(
            self,
            id: UUID4,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by user ID."""
        return await delete_account(self, id)

    async def get(
            self,
            identifier: str,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ):
        """Get user account by user ID."""
        return await get_account(self, identifier)

    async def get_authenticated_user(
            self,
            current_user: Annotated[CurrentAccountPayload, Depends(get_current_user)] = None,
    ) -> CurrentAccountOut:
        """Get the authenticated user account details"""
        return await get_authenticated_user(self, current_user)


user_account_service = UserAccountService(
    repository=user_account_repo,
    out_schema=UserAccountOut
)
