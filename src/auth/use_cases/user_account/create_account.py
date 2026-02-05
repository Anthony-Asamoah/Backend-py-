from fastapi import BackgroundTasks, HTTPException

from auth.repositories import password_reset_token_repo
from auth.schemas.user_account import UserAccountCreate, IdentifierChoices, UserAccountRepoCreate
from auth.utils import detect_identifier_type
from auth.utils.password_hasher import Hasher
from main import settings
from main.utils.logger import log
from main.utils.validators import validate_phone_number
from notification.schemas.notification import NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel
from user_info.use_cases import user_info_service


async def create_account(cls, payload: UserAccountCreate, background_tasks: BackgroundTasks):
    log.debug(f'init new user_info with payload: {payload}')

    # validate identifier type
    identifier_type = detect_identifier_type(payload.identifier)

    # parse phone number
    if identifier_type == IdentifierChoices.PHONE_NUMBER:
        payload.identifier = validate_phone_number(payload.identifier)

    # check if account already exists with this exact identifier
    account = await cls.repo.get_by_identifier(payload.identifier)
    if account: raise HTTPException(status_code=400, detail='Account already exists')

    # check if user profile exists with this account
    user_info = await user_info_service.repo.get_user_by_email_or_phone_number(
        email=payload.identifier, phone_number=payload.identifier
    )

    if user_info and not account:
        # check if there's already an account linked to this user profile
        existing_account = await cls.repo.get_by_id(id=user_info.id)
        # determine which identifier was used for the existing account
        opposite_field = 'phone number' if identifier_type == IdentifierChoices.EMAIL else 'email'
        if existing_account: raise HTTPException(
            status_code=400,
            detail=f'Account already exists for this profile. Try logging in with your {opposite_field} instead.'
        )

        # check for account using the opposite identifier from the user profile
        if identifier_type == IdentifierChoices.EMAIL:
            # user is signing up with email, check if account exists with their phone
            existing_account = await cls.repo.get_by_identifier(user_info.phone_number)
            if existing_account: raise HTTPException(
                status_code=400,
                detail='Account already exists for this profile. Try logging in with your phone number instead.'
            )
        else:
            # user is signing up with phone, check if account exists with their email
            existing_account = await cls.repo.get_by_identifier(user_info.email)
            if existing_account: raise HTTPException(
                status_code=400,
                detail='Account already exists for this profile. Try logging in with your email instead.'
            )

    new_account_payload = UserAccountRepoCreate(**payload.model_dump())

    # link to existing user profile if found
    if user_info: new_account_payload.id = user_info.id

    # hash password
    new_account_payload.password = Hasher.get_password_hash(payload.password)

    # create account record
    new_account = await cls.repo.create(new_account_payload)

    # create verification token (using password reset token for verification)
    verification_token = await password_reset_token_repo.create(new_account.cursor)
    log.info(f'generated verification token: {verification_token}')

    # Send welcome and verification notifications
    if background_tasks:
        from notification.use_cases.notification import notification_service

        # Get user info for notification context
        if not user_info:
            user_info = await user_info_service.repo.get_by_id(new_account.user_info_id)

        if user_info:
            # Determine notification channel based on identifier type
            channel = NotificationChannel.EMAIL if identifier_type == IdentifierChoices.EMAIL else NotificationChannel.SMS

            # Get user name for notifications
            user_name = f"{user_info.first_name} {user_info.last_name}".strip() or payload.identifier

            # Calculate verification token expiry time
            expiry_hours = settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            expiry_time = f"{expiry_hours} hours" if expiry_hours > 1 else f"{expiry_hours} hour"

            try:
                # 1. Send welcome notification
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="USER-ONBOARDING",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "email": payload.identifier if identifier_type == IdentifierChoices.EMAIL else user_info.email or "N/A"
                        },
                        channels=[channel, NotificationChannel.WEBSOCKET],
                        links=[{
                            "label": "Verify Account",
                            "url": f"{settings.APP_HOST}/verify-account?token={verification_token}"
                        }]
                    ),
                    current_user=new_account,
                    background_tasks=background_tasks
                )
                log.info(f'Welcome notification sent to {payload.identifier} via {channel}')

                # 2. Send verification notification
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="EMAIL-VERIFICATION",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "verification_code": verification_token,
                            "expiry_time": expiry_time
                        },
                        channels=[channel],
                        links=[{
                            "label": "Verify Now",
                            "url": f"{settings.APP_HOST}/verify-account?token={verification_token}"
                        }]
                    ),
                    current_user=new_account,
                    background_tasks=background_tasks
                )
                log.info(f'Verification notification sent to {payload.identifier} via {channel}')

            except Exception as e:
                log.error(f'Failed to send account creation notifications: {e}')
                # Don't fail the request if notification fails
        else:
            log.warning(f'User info not found for account {new_account.id}, skipping notifications')

    return await cls.to_domain(new_account)
