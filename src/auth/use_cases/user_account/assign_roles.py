from fastapi import HTTPException
from pydantic import UUID4

from auth.use_cases import user_account_service


async def assign_roles(cls, user_id: UUID4, role_ids: list[UUID4]) -> None:
    account = user_account_service.repo.get_by_id(user_id)
    if not account: raise HTTPException(status_code=404)

    is_updated = await user_account_service.repo.assign_roles(user_id, role_ids)
    if not is_updated: raise HTTPException(status_code=400, detail='Failed to assign roles')
