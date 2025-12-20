from fastapi import HTTPException

from main.utils.logger import log


async def get_account(self, identifier: str):
    log.debug(f'init get user account with id: {identifier}')

    obj = await self.repo.get_by_identifier(identifier)
    if not obj: raise HTTPException(status_code=404)
    return await self.to_domain(obj)
