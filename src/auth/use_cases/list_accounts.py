from django.contrib.postgres.search import SearchVector
from fastapi import HTTPException

from auth.schema import UserAccountOut
from main.utils.logger import log


async def list_accounts(
        cls,
        current_user: UserAccountOut,
        search: str = None,
        identifier: str = None,
        is_deleted: bool = None,
        skip: int = 0,
        limit: int = 100,
) -> list:
    log.debug(f'init list user accounts with skip: {skip}, limit: {limit}')

    query = cls.repo.all()

    if is_deleted is not None: query = query.filter(is_deleted=is_deleted)

    if identifier and search: raise HTTPException(
        status_code=400, detail='Search and identifier are mutually exclusive'
    )

    if identifier:
        obj = await query.filter(identifier=identifier).afirst()
        return [obj]

    search_fields = ['identifier']
    if search:
        results = query.annotate(search=SearchVector(*search_fields)).filter(search=search)
        return await cls.evaluate_queryset(results, skip, limit)

    return await cls.evaluate_queryset(query, skip, limit)
