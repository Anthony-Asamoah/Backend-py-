from typing import Annotated

from fastapi import HTTPException, Depends, status

from auth.models import UserAccount
from auth.utils import get_current_user


def check_user_role(roles: list[str]):
    async def role_check(
            account: Annotated[UserAccount, Depends(get_current_user)],
    ):
        user_roles = account.get_roles()
        available_roles = set(role.upper() for role in roles) & set(role.upper() for role in user_roles)

        if not available_roles: raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required permissions to perform this action"
        )
        return available_roles

    return role_check
