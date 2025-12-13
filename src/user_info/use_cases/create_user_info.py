from django.db.models import Q
from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoCreate


async def create_user_info(cls, payload: UserInfoCreate):
    log.debug(f'init new user_info with payload: {payload}')

    # validate unique email and phone number
    existing_user_info = await cls.repo.filter(
        Q(email=payload.email) | Q(phone_number=payload.phone_number)
    ).afirst()
    if existing_user_info:
        raise HTTPException(status_code=400, detail=f'Already saved {existing_user_info}')

    new_user_info_payload = {**payload.model_dump()}

    # use the id of an existing account (if any)
    from auth.use_cases import user_account_service
    existing_account = await user_account_service.repo.filter(
        Q(identifier=payload.email) | Q(identifier=payload.phone_number)
    ).afirst()
    if existing_account: new_user_info_payload['id'] = existing_account.id

    new_user_info = await cls.repo.acreate(**new_user_info_payload)
    return cls.to_domain(new_user_info)
