from django.contrib.postgres.search import SearchVector
from fastapi import HTTPException

from main.utils.logger import log


async def list_user_info(
        cls,
        search: str = None,
        id: str = None,
        skip: int = 0,
        limit: int = 100
) -> list:
    log.debug(f'init list users with skip: {skip}, limit: {limit}')

    if id and search:
        raise HTTPException(status_code=400, detail='Search and id are mutually exclusive')

    if id:
        user = await cls.get(id)
        return [user]

    search_fields = ['first_name', 'last_name', 'other_names', 'email', 'phone_number']
    if search:
        results = cls.repo.annotate(search=SearchVector(*search_fields)).filter(search=search)
        return await cls.evaluate_queryset(results, skip, limit)

    query = cls.repo.all()
    return await cls.evaluate_queryset(query, skip, limit)
