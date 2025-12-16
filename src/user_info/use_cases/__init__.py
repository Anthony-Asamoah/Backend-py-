from typing import Annotated

from fastapi import Depends

from auth.schema import UserAccountOut
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from user_info.models import UserInfo
from user_info.schema import UserInfoOut, UserInfoCreate, UserInfoUpdate
from .create_user_info import create_user_info
from .delete_user_info import delete_user_info
from .get_user_info import get_user_info
from .list_user_info import list_user_info
from .update_user_info import update_user_info
from ..repository import UserInfoRepository


class UserInfoService(BaseService[UserInfo, UserInfoOut]):
    """Methods to handle user info domain operations."""

    async def create(
            self,
            payload: UserInfoCreate,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Create a new profile with a user's information."""
        return await create_user_info(self, payload)

    async def read(
            self,
            search: str = None,
            id: str = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of users information."""
        return await list_user_info(self, search, id, skip, limit)

    async def update(
            self,
            id: str,
            payload: UserInfoUpdate,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Update user information with partial data."""
        return await update_user_info(self, id, payload)

    async def delete(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by user ID."""
        return await delete_user_info(self, id)

    async def get(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Get user info by user ID."""
        return await get_user_info(self, id)


user_info_service = UserInfoService(
    repository=UserInfoRepository(UserInfo),
    out_schema=UserInfoOut
)
