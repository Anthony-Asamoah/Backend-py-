from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException
from pyasn1.codec.ber.decoder import PrintableStringPayloadDecoder
from pydantic_core import PydanticCustomError

from auth.schema import UserAccountLogin, UserAccountLoginOut, IdentifierChoices
from auth.utils import authenticate_account, create_access_token, create_refresh_token, detect_identifier_type
from main.utils.logger import log
from main.utils.validators import validate_phone_number
from user_info.use_cases import user_info_service


async def login(cls, payload: UserAccountLogin) -> UserAccountLoginOut:
    log.debug(f'init new user_info with payload: {payload}')

    msg = 'Invalid credentials provided'
    try:
        identifier_type = detect_identifier_type(payload.identifier)

        # parse phone number
        if identifier_type == IdentifierChoices.PHONE_NUMBER:
            payload.identifier = validate_phone_number(payload.identifier)

        # get profile
        profile = await user_info_service.repo.get_user_by_email_or_phone_number(**{
            f'{identifier_type.name.lower()}': payload.identifier
        })

        # get account by identifier
        account = await cls.repo.get_by_identifier(payload.identifier)
        if not account and profile:
            # allow a user to log in with either email or phone number
            # if account not found by identifier, try finding by profile id
            account = await cls.repo.get_by_id(profile.id)

        is_authenticated = await authenticate_account(account, payload.password)
        if not is_authenticated: raise HTTPException(status_code=400, detail=msg)

        # get profile
        profile = await user_info_service.repo.get_by_id(account.id)

        return UserAccountLoginOut(
            access_token=await create_access_token({"sub": account.identifier}),
            refresh_token=await create_refresh_token({"sub": account.identifier}),
            user_info=profile
        )

    except (PydanticCustomError, ValueError, ObjectDoesNotExist):
        raise HTTPException(status_code=400, detail=msg)
