from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException
from pydantic_core import PydanticCustomError

from auth.schema import UserAccountLogin, UserAccountLoginOut
from auth.utils import authenticate_account, create_access_token, create_refresh_token, detect_identifier_type
from main.utils.logger import log
from user_info.use_cases import user_info_service


async def login(cls, payload: UserAccountLogin) -> UserAccountLoginOut:
    log.debug(f'init new user_info with payload: {payload}')

    msg = 'Invalid credentials provided'
    try:
        identifier_type = detect_identifier_type(payload.identifier)

        # get profile
        profile = await user_info_service.repo.filter(**{
            f'{identifier_type.name.lower()}': payload.identifier
        }).afirst()

        # get account by identifier
        account = await cls.repo.filter(identifier=payload.identifier).afirst()
        if not account and profile:
            # allow a user to log in with either email or phone number
            # if account not found by identifier, try finding by profile id
            account = await cls.repo.filter(id=profile.id).afirst()

        is_authenticated = await authenticate_account(account, payload.password)
        if not is_authenticated: raise HTTPException(status_code=400, detail=msg)

        # get profile
        profile = await user_info_service.repo.filter(id=account.id).afirst()

        return UserAccountLoginOut(
            access_token=await create_access_token({"sub": account.identifier}),
            refresh_token=await create_refresh_token({"sub": account.identifier}),
            user_info=profile
        )

    except (PydanticCustomError, ValueError, ObjectDoesNotExist):
        raise HTTPException(status_code=400, detail=msg)
