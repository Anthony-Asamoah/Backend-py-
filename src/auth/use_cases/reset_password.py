from fastapi import HTTPException, BackgroundTasks

from auth.schema import ResetPassword


async def reset_password(cls, payload: ResetPassword, background_tasks: BackgroundTasks = None) -> None:
    from auth.repositories import password_reset_token_repo
    token_obj = await password_reset_token_repo.get_by_token(payload.token)
    if not token_obj: raise HTTPException(status_code=400, detail='Invalid reset token')

    from auth.use_cases import user_account_service
    await user_account_service.repo.change_password(id=token_obj.user_account.id, password=payload.password)

    await token_obj.adelete()

    # background_tasks.add_task(send_change_password_notification)
