from fastapi import BackgroundTasks, HTTPException

from auth.repositories import revoked_token_repo
from auth.schemas.user_account import IdentifierChoices, Token
from auth.utils import detect_identifier_type
from main import settings
from main.utils.logger import log
from notification.schemas.notification import NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel


async def activate_account(cls, payload: Token, background_tasks: BackgroundTasks) -> None:
    log.debug(f'init new activate account with payload: {payload}')

    token_obj = await revoked_token_repo.get_by_token(payload.token)
    if not token_obj: raise HTTPException(status_code=404)

    await cls.repo.activate_account(token_obj.user_account.id)

    # Send activation confirmation notification
    if background_tasks:
        from notification.use_cases.notification import notification_service
        from user_info.use_cases import user_info_service

        try:
            # Get account and user info
            account = token_obj.user_account
            user_info = await user_info_service.repo.get_by_id(account.user_info_id)

            if user_info:
                # Determine identifier type from account
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

                # Send activation confirmation
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="USER-ONBOARDING",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "email": identifier if identifier_type == IdentifierChoices.EMAIL else user_info.email or "N/A"
                        },
                        channels=[channel, NotificationChannel.WEBSOCKET],
                        links=[{
                            "label": "Get Started",
                            "url": f"{settings.APP_HOST}/dashboard"
                        }]
                    ),
                    current_user=account,
                    background_tasks=background_tasks
                )
                log.info(f'Activation confirmation sent to {identifier} via {channel}')

            else:
                log.warning(f'User info not found for account {account.id}')

        except Exception as e:
            log.error(f'Failed to send activation confirmation: {e}')
            # Don't fail the request if notification fails
