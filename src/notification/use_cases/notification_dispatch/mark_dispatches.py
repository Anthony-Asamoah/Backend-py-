from typing import List

from pydantic import UUID4

from main.utils.logger import log


async def mark_as_sent(cls, id: UUID4, extra_info=None) -> bool:
    log.debug(f'init mark_as_sent for dispatch_id: {id}')
    return await cls.repo.mark_as_sent(id=id, extra_info=extra_info)


async def bulk_mark_as_sent(cls, ids: List[UUID4], extra_info=None) -> bool:
    log.debug(f'init bulk_mark_as_sent for {len(ids)} dispatches')
    return await cls.repo.bulk_mark_as_sent(ids=ids, extra_info=extra_info)


async def mark_as_delivered(cls, id: UUID4, extra_info=None) -> bool:
    log.debug(f'init mark_as_delivered for dispatch_id: {id}')
    return await cls.repo.mark_as_delivered(id=id, extra_info=extra_info)


async def bulk_mark_as_delivered(cls, ids: List[UUID4], extra_info=None) -> bool:
    log.debug(f'init bulk_mark_as_delivered for {len(ids)} dispatches')
    return await cls.repo.bulk_mark_as_delivered(ids=ids, extra_info=extra_info)


async def mark_as_read(cls, id: UUID4, extra_info=None) -> bool:
    log.debug(f'init mark_as_read for dispatch_id: {id}')
    return await cls.repo.mark_as_read(id=id, extra_info=extra_info)


async def bulk_mark_as_read(cls, ids: List[UUID4], extra_info=None) -> bool:
    log.debug(f'init bulk_mark_as_read for {len(ids)} dispatches')
    return await cls.repo.bulk_mark_as_read(ids=ids, extra_info=extra_info)


async def mark_as_failed(cls, id: UUID4, error_message: str) -> bool:
    log.debug(f'init mark_as_failed for dispatch_id: {id}')
    return await cls.repo.mark_as_failed(id=id, error_message=error_message)


async def bulk_mark_as_failed(cls, ids: List[UUID4], error_message: str) -> bool:
    log.debug(f'init bulk_mark_as_failed for {len(ids)} dispatches')
    return await cls.repo.bulk_mark_as_failed(ids=ids, error_message=error_message)