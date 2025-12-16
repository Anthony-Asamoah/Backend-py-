from django.db.models import Q
from fastapi import HTTPException

from main.utils.logger import log
from user_info.schema import UserInfoCreate, UserInfoRepoCreate, UserInfoOut


async def create_user_info(cls, payload: UserInfoCreate) -> UserInfoOut:
    log.debug(f'init new user_info with payload: {payload}')

    # validate unique email and phone number
    existing_user_info = await cls.repo.get_user_by_email_or_phone_number(
        email=payload.email, phone_number=payload.phone_number
    )
    if existing_user_info: raise HTTPException(
        status_code=400, detail=f'Already saved {existing_user_info}'
    )

    new_user_info_payload = UserInfoRepoCreate(**payload.model_dump())

    # use the id of an existing account (if any)
    from auth.use_cases import user_account_service  # todo: user account repository
    existing_account = await user_account_service.repo.filter(
        Q(identifier=payload.email) | Q(identifier=payload.phone_number)
    ).afirst()
    if existing_account: new_user_info_payload.id = existing_account.id

    new_user_info = await cls.repo.create(new_user_info_payload)
    return await cls.to_domain(new_user_info)
