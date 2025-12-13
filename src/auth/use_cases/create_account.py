from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from fastapi import BackgroundTasks, HTTPException

from auth.schema import UserAccountCreate, IdentifierChoices
from auth.utils import detect_identifier_type
from auth.utils.authenticate_user import Hasher
from main.utils.logger import log
from main.utils.validators import validate_phone_number
from user_info.use_cases import user_info_service


async def create_account(cls, payload: UserAccountCreate, background_tasks: BackgroundTasks):
    log.debug(f'init new user_info with payload: {payload}')

    # validate identifier type
    identifier_type = detect_identifier_type(payload.identifier)

    # parse phone number
    if identifier_type == IdentifierChoices.PHONE_NUMBER:
        payload.identifier = validate_phone_number(payload.identifier)

    # check if account already exists with this exact identifier
    account = await cls.repo.filter(identifier=payload.identifier).afirst()
    if account: raise HTTPException(status_code=400, detail='Account already exists')

    # check if user profile exists with this account
    user_info = await user_info_service.repo.filter(
        Q(email=payload.identifier) | Q(phone_number=payload.identifier)
    ).afirst()

    if user_info and not account:
        # check if there's already an account linked to this user profile
        existing_account = await cls.repo.filter(id=user_info.id).afirst()
        # determine which identifier was used for the existing account
        opposite_field = 'phone number' if identifier_type == IdentifierChoices.EMAIL else 'email'
        if existing_account: raise HTTPException(
            status_code=400,
            detail=f'Account already exists for this profile. Try logging in with your {opposite_field} instead.'
        )

        # check for account using the opposite identifier from the user profile
        if identifier_type == IdentifierChoices.EMAIL:
            # user is signing up with email, check if account exists with their phone
            existing_account = await cls.repo.filter(identifier=user_info.phone_number).afirst()
            if existing_account: raise HTTPException(
                status_code=400,
                detail='Account already exists for this profile. Try logging in with your phone number instead.'
            )
        else:
            # user is signing up with phone, check if account exists with their email
            existing_account = await cls.repo.filter(identifier=user_info.email).afirst()
            if existing_account: raise HTTPException(
                status_code=400,
                detail='Account already exists for this profile. Try logging in with your email instead.'
            )

    new_account_payload = {**payload.model_dump(), 'identifier_type': identifier_type.name}

    # link to existing user profile if found
    if user_info: new_account_payload['id'] = user_info.id

    # hash password
    new_account_payload['password'] = Hasher.get_password_hash(payload.password)

    # create account record
    new_account = await cls.repo.acreate(**new_account_payload)

    # trigger notifications
    if identifier_type == IdentifierChoices.EMAIL:
        # background_tasks.add_task(send_otp_email)
        pass

    elif identifier_type == IdentifierChoices.PHONE_NUMBER:
        # background_tasks.add_task(send_otp_sms)
        pass

    else:
        raise ImproperlyConfigured(f'Invalid identifier type: {payload.identifier_type}')

    return cls.to_domain(new_account)
