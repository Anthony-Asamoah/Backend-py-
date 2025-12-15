from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException, BackgroundTasks

from auth.schema import ChangePassword
from auth.utils.password_hasher import Hasher


async def change_password(cls, id: str, payload: ChangePassword, background_tasks: BackgroundTasks = None) -> None:
    try:
        account = await cls.repo.aget(id=id)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
    else:
        account.password = Hasher.get_password_hash(payload.password)
        await account.asave()
        # background_tasks.add_task(send_change_password_notification)
