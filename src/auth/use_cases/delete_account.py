from fastapi import HTTPException

from main.utils.logger import log


async def delete_account(self, id: str) -> None:
    log.debug(f'init delete user account {id}')

    account = await self.repo.get_by_id(id=id)
    if not account: raise HTTPException(status_code=404)

    await self.repo.update(id, {'is_deleted': True})
