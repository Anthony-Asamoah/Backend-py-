from typing import Annotated

from fastapi import BackgroundTasks, Depends
from fastapi.security import HTTPAuthorizationCredentials

from main import settings
from main.utils.base_classes import BaseService
from .activate_account import activate_account
from .change_password import change_password
from .create_account import create_account
from .delete_account import delete_account
from .get_account import get_account
from .list_accounts import list_accounts
from .login import login
from .logout import logout
from .refresh_token import get_new_access_tokens
from .reset_password import reset_password
from .reset_password_request import reset_password_request
from ..models import UserAccount
from ..repository import UserAccountRepository
from ..schema import (
    UserAccountCreate, UserAccountOut, UserAccountLogin,
    RefreshToken, Token,
    ChangePassword, ResetPassword
)
from ..utils import get_current_user


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
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """change account password."""
        await change_password(self, str(current_user.id), payload, tasks)

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

    async def read(
            self, *,
            search: str = None,
            identifier: str = None,
            is_deleted: bool = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of user accounts."""
        return await list_accounts(self, current_user, search, identifier, is_deleted, skip, limit)

    async def delete(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by user ID."""
        return await delete_account(self, id)

    async def get(
            self,
            identifier: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Get user account by user ID."""
        return await get_account(self, identifier)


user_account_service = UserAccountService(
    repository=UserAccountRepository(UserAccount),
    out_schema=UserAccountOut
)
