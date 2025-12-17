from typing import Annotated, Set

from fastapi import HTTPException, Depends, status

from auth.schemas.user_account import CurrentAccountPayload
from auth.use_cases.role import role_service
from auth.utils import get_current_user
from main.utils.logger import log


def check_user_role(roles: list[str]):
    """
    Dependency to check if user has any of the required roles.

    Args:
        roles: List of role names (case-insensitive)

    Returns:
        Set of matching roles

    Raises:
        HTTPException: 403 if user doesn't have any of the required roles
    """
    async def role_check(
        account: Annotated[CurrentAccountPayload, Depends(get_current_user)]
    ) -> Set[str]:
        # Get user's roles
        account_role_objs = await role_service.get_user_roles(user_id=str(account.id))

        # Normalize role names for comparison (case-insensitive)
        required_roles = {role.upper() for role in roles}
        user_roles = {role.name.upper() for role in account_role_objs}

        # Find matching roles
        available_roles = required_roles & user_roles

        if not available_roles:
            log.warning(
                f'User {account.identifier} attempted to access endpoint requiring roles {roles}. '
                f'User has roles: {[r.name for r in account_role_objs]}'
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}"
            )

        return available_roles

    return role_check


def check_user_permission(permissions: list[str]):
    """
    Dependency to check if user has any of the required permissions.
    Supports wildcard permissions (e.g., 'user_account.*' matches 'user_account.create').

    Args:
        permissions: List of permission names (e.g., ['user_account.create', 'user_account.*'])

    Returns:
        Set of matching permissions

    Raises:
        HTTPException: 403 if user doesn't have any of the required permissions
    """
    async def permission_check(
        account: Annotated[CurrentAccountPayload, Depends(get_current_user)]
    ) -> Set[str]:
        # Get user's roles with permissions
        account_role_objs = await role_service.get_user_roles(user_id=str(account.id))

        # Flatten all permissions from all roles
        user_permissions = set()
        for role in account_role_objs:
            for perm in role.permissions:
                user_permissions.add(perm.name.lower())

        # Check for matching permissions (including wildcard support)
        available_permissions = set()
        for required_perm in permissions:
            required_perm_lower = required_perm.lower()

            # Direct match
            if required_perm_lower in user_permissions:
                available_permissions.add(required_perm)
                continue

            # Wildcard match (e.g., user has 'user_account.*', needs 'user_account.create')
            resource = required_perm_lower.rsplit('.', 1)[0] if '.' in required_perm_lower else required_perm_lower
            wildcard = f"{resource}.*"
            if wildcard in user_permissions:
                available_permissions.add(required_perm)
                continue

            # Check if user has wildcard and required is specific
            # (e.g., user needs 'user_account.*', has 'user_account.create')
            if required_perm_lower.endswith('.*'):
                if any(p.startswith(resource + '.') for p in user_permissions):
                    available_permissions.add(required_perm)
                    continue

        if not available_permissions:
            log.warning(
                f'User {account.identifier} attempted to access endpoint requiring permissions {permissions}. '
                f'User has permissions: {list(user_permissions)}'
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission(s): {', '.join(permissions)}"
            )

        return available_permissions

    return permission_check
