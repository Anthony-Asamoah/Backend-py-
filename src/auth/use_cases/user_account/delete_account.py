from pydantic import UUID4

from main.utils.logger import log


async def delete_account(self, id: UUID4) -> None:
    log.debug(f'init delete user account {id}')

    await self.get(id)
    await self.repo.update(id, {'is_deleted': True})
