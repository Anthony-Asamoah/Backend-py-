from fastapi import BackgroundTasks, HTTPException

from auth.repository import password_reset_token_repo
from auth.schema import IdentifierChoices
from auth.utils import detect_identifier_type
from main.utils.logger import log
from main.utils.validators import validate_phone_number


async def reset_password_request(cls, identifier: str, background_tasks: BackgroundTasks = None) -> None:
    try:
        identifier_type = detect_identifier_type(identifier)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid phone or email given')
    else:
        if identifier_type == IdentifierChoices.PHONE_NUMBER:
            identifier = validate_phone_number(identifier)

        from auth.use_cases import user_account_service
        account = await user_account_service.repo.get_by_identifier(identifier)
        if not account: raise HTTPException(status_code=204)

        reset_token = await password_reset_token_repo.create(account.cursor)
        log.info(f'generated reset token: {reset_token}')
        if identifier_type == IdentifierChoices.EMAIL:
            # background_tasks.add_task(send_change_password_notification)
            pass
        if identifier_type == IdentifierChoices.PHONE_NUMBER:
            # background_tasks.add_task(send_change_password_notification)
            pass
