from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log


async def get_account(self, identifier: str):
    log.debug(f'init get user account with id: {identifier}')

    try:
        obj = await self.repo.aget(identifier=identifier)
        return self.to_domain(obj)

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404)
