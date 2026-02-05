from fastapi import BackgroundTasks, HTTPException

from auth.repositories import password_reset_token_repo
from auth.schemas.user_account import IdentifierChoices
from auth.utils import detect_identifier_type
from main import settings
from main.utils.logger import log
from main.utils.validators import validate_phone_number
from notification.schemas.notification import NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel


async def reset_password_request(cls, identifier: str, background_tasks: BackgroundTasks = None) -> None:
    try:
        identifier_type = detect_identifier_type(identifier)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid phone or email given')
    else:
        if identifier_type == IdentifierChoices.PHONE_NUMBER:
            identifier = validate_phone_number(identifier)

        from auth.use_cases import user_account_service
        from user_info.use_cases import user_info_service
        from notification.use_cases.notification import notification_service

        account = await user_account_service.repo.get_by_identifier(identifier)
        if not account: raise HTTPException(status_code=204)

        # Get user info for notification
        user_info = await user_info_service.repo.get_by_id(account.user_info_id)
        if not user_info:
            log.warning(f'User info not found for account {account.id}')

        reset_token = await password_reset_token_repo.create(account.cursor)
        log.info(f'generated reset token: {reset_token}')

        # Send password reset notification
        if background_tasks and user_info:
            # Determine channel based on identifier type
            channel = NotificationChannel.EMAIL if identifier_type == IdentifierChoices.EMAIL else NotificationChannel.SMS

            # Get user name for notification
            user_name = f"{user_info.first_name} {user_info.last_name}".strip() or identifier

            # Calculate expiry time
            expiry_hours = settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            expiry_time = f"{expiry_hours} hours" if expiry_hours > 1 else f"{expiry_hours} hour"

            try:
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="PASSWORD-RESET",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "reset_token": reset_token,
                            "expiry_time": expiry_time
                        },
                        channels=[channel],
                        links=[{
                            "label": "Reset Password",
                            "url": f"{settings.APP_HOST}/reset-password?token={reset_token}"
                        }]
                    ),
                    current_user=account,
                    background_tasks=background_tasks
                )
                log.info(f'Password reset notification sent to {identifier} via {channel}')
            except Exception as e:
                log.error(f'Failed to send password reset notification: {e}')
                # Don't fail the request if notification fails
