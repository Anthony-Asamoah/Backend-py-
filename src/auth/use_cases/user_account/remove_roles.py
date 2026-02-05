from datetime import datetime

from fastapi import HTTPException, BackgroundTasks
from pydantic import UUID4

from auth.schemas.user_account import IdentifierChoices
from auth.utils import detect_identifier_type
from main import settings
from main.utils.logger import log
from notification.schemas.notification import NotificationCreate
from notification.schemas.notification_dispatch import NotificationChannel


async def remove_roles(
        cls,
        user_id: UUID4,
        role_ids: list[UUID4],
        background_tasks: BackgroundTasks = None,
        removed_by_name: str = "Administrator"
) -> None:
    from auth.use_cases import user_account_service

    account = await user_account_service.repo.get_by_id(user_id)
    if not account: raise HTTPException(status_code=404)

    is_updated = await user_account_service.repo.remove_roles(user_id, role_ids)
    if not is_updated: raise HTTPException(status_code=400, detail='Failed to remove roles')

    # Send role removal notification
    if background_tasks and role_ids:
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

                # Determine notification channel (EMAIL + WEBSOCKET for real-time)
                channel = NotificationChannel.EMAIL if identifier_type == IdentifierChoices.EMAIL else NotificationChannel.SMS

                # Get user name
                user_name = f"{user_info.first_name} {user_info.last_name}".strip() or identifier

                # Format removed roles
                # Note: role_ids are UUIDs - in a real scenario, you'd fetch role names from the database
                roles_removed_list = f"<ul>{''.join([f'<li>Role {str(role_id)[:8]}</li>' for role_id in role_ids])}</ul>"

                # Format removal date
                removal_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

                # Send role removal notification
                await notification_service.create(
                    payload=NotificationCreate(
                        template_name="ROLE-REMOVED",
                        context={
                            "user_name": user_name,
                            "platform_name": settings.APP_TITLE,
                            "roles_removed": roles_removed_list,
                            "removed_by": removed_by_name,
                            "removal_date": removal_date,
                            "impact_explanation": "Some features and capabilities may no longer be accessible with your current permissions. If you need access to these features, please contact your administrator."
                        },
                        channels=[channel, NotificationChannel.WEBSOCKET],
                        links=[{
                            "label": "View Permissions",
                            "url": f"{settings.APP_HOST}/profile/permissions"
                        }]
                    ),
                    current_user=account,
                    background_tasks=background_tasks
                )
                log.info(f'Role removal notification sent to {identifier} via {channel}')

            else:
                log.warning(f'User info not found for account {account.id}')

        except Exception as e:
            log.error(f'Failed to send role removal notification: {e}')
            # Don't fail the request if notification fails
