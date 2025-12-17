from fastapi import HTTPException, BackgroundTasks
from pydantic import UUID4

from auth.schemas.password_reset_token import ChangePassword


async def change_password(cls, id: UUID4, payload: ChangePassword, background_tasks: BackgroundTasks = None) -> None:
    account = await cls.repo.get_by_id(id)
    if not account: raise HTTPException(status_code=404)

    await cls.repo.change_password(account.id, payload.password)
    # background_tasks.add_task(send_change_password_notification)
