from typing import TypeVar, Generic, List, Type, Optional, Union
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.contrib.postgres.search import SearchVector
from django.db import models
from pydantic import BaseModel as PydanticBaseModel, UUID4

from main.utils.logger import log

ModelType = TypeVar("ModelType", bound=models.Model)
OutSchemaType = TypeVar("OutSchemaType", bound=PydanticBaseModel)
RepositoryInSchemaType = TypeVar("RepositoryInSchemaType", bound=PydanticBaseModel)


class BaseOutSchema(PydanticBaseModel):
    id: UUID4

    class Config:
        from_attributes = True


class BaseModel(models.Model):
    cursor = models.BigAutoField(editable=False, db_index=True, primary_key=True)
    id = models.UUIDField(default=uuid4, editable=False, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cursor']
        abstract = True


class BaseRepository(Generic[ModelType,]):
    def __init__(self, model: Type[ModelType], search_fields: list[str] = None):
        self.model = model
        self.manager = model.objects
        self.search_fields = search_fields or []

    async def paginate_queryset(self, queryset, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Paginate and convert from Django model instance to Pydantic schema."""
        result = await sync_to_async(list)(queryset.filter(cursor__gt=skip)[:limit])
        return result

    async def delete(self, id: UUID4) -> bool:
        log.debug(f'init delete {self.model.__name__} by id {id}')
        result = await self.model.objects.filter(id=id).adelete()
        is_deleted = bool(result[0])
        return is_deleted

    async def create(self, payload: RepositoryInSchemaType) -> ModelType:
        log.debug(f'init create {self.model.__name__}')
        return await self.model.objects.acreate(**payload.model_dump())

    async def update(self, id: UUID4, payload: Union[dict, RepositoryInSchemaType]) -> Optional[ModelType]:
        log.debug(f'init update {self.model.__name__} with id: {id}')
        obj = await self.get_by_id(id=id)
        if not obj: return None

        if isinstance(payload, PydanticBaseModel):
            payload = payload.model_dump(exclude_unset=True)

        for field, value in payload.items():
            setattr(obj, field, value)

        await obj.asave()
        await obj.arefresh_from_db()
        return obj

    async def get_by_id(self, id: UUID4) -> Optional[ModelType]:
        log.debug(f'init get {self.model.__name__} by id: {id}')
        return await self.model.objects.filter(id=id).afirst()

    async def list(self, search: str = None, skip: int = 0, limit: int = 100) -> list[ModelType]:
        log.debug(f'init list user info with skip: {skip}, limit: {limit}')
        query = self.model.objects.all()

        if search:
            results = query.annotate(search=SearchVector(*self.search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        result = await self.paginate_queryset(query, skip, limit)
        return result


class BaseService(Generic[ModelType, OutSchemaType]):
    def __init__(self, repository: BaseRepository, out_schema: Type[OutSchemaType]):
        self.repo = repository
        self.out_schema = out_schema

    async def to_domain(self, obj, list=False) -> OutSchemaType:
        """Convert Django model instance to Pydantic schema."""
        if list: return [self.out_schema.model_validate(_) for _ in obj]
        return self.out_schema.model_validate(obj)
