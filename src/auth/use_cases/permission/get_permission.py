from pydantic import UUID4

from main.utils.logger import log


async def get_permission(cls, id: UUID4) -> PermissionError:
    log.debug(f'init get permission with id: {id}')

    permission = await cls.repo.get_by_id(id)
    return await cls.to_domain(permission)
