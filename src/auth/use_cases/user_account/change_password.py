from datetime import datetime

from fastapi import HTTPException, BackgroundTasks
from pydantic import UUID4

from auth.schemas.password_reset_token import ChangePassword
from auth.schemas.user_account import IdentifierChoices
from auth.utils import detect_identifier_type
from main import settings
from main.utils.logger import log
from notification.schemas.notification import NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel


async def change_password(cls, id: UUID4, payload: ChangePassword, background_tasks: BackgroundTasks = None) -> None:
    account = await cls.repo.get_by_id(id)
    if not account: raise HTTPException(status_code=404)

    await cls.repo.change_password(account.id, payload.password)

    # Send password change notification
    if background_tasks:
        from notification.use_cases.notification import notification_service
        from user_info.use_cases import user_info_service

        try:
            # Get user info
            user_info = await user_info_service.repo.get_by_id(account.user_info_id)

            if user_info:
                # Determine identifier from account
                identifier = account.email or account.phone_number
                if not identifier:
                    log.warning(f'No identifier found for account {account.id}')
                    return

                try:
                    identifier_type = detect_identifier_type(identifier)
                except ValueError:
                    log.warning(f'Could not detect identifier type for {identifier}')
                    identifier_type = IdentifierChoices.EMAIL  # Default to email

                # Determine notification channel
                channel = NotificationChannel.EMAIL if identifier_type == IdentifierChoices.EMAIL else NotificationChannel.SMS

                # Get user name
                user_name = f"{user_info.first_name} {user_info.last_name}".strip() or identifier

                # Format change time
                change_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

                # Send password changed notification
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="PASSWORD-CHANGED",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "change_time": change_time,
                            "support_email": settings.SUPPORT_EMAIL if hasattr(settings, 'SUPPORT_EMAIL') else "support@example.com"
                        },
                        channels=[channel],
                        links=[{
                            "label": "Contact Support",
                            "url": f"{settings.APP_HOST}/support"
                        }]
                    ),
                    current_user=account,
                    background_tasks=background_tasks
                )
                log.info(f'Password change notification sent to {identifier} via {channel}')

            else:
                log.warning(f'User info not found for account {account.id}')

        except Exception as e:
            log.error(f'Failed to send password change notification: {e}')
            # Don't fail the request if notification fails
