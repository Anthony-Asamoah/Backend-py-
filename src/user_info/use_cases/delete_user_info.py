from fastapi import HTTPException

from main.utils.logger import log


async def delete_user_info(cls, id: str) -> None:
    log.debug(f'init delete user_info {id}')

    is_deleted = await cls.repo.delete(id=id)
    if not is_deleted: raise HTTPException(status_code=404)
