import uuid
from typing import TypeVar, Generic, List, Type, Union
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.db import models
from pydantic import BaseModel as PydanticBaseModel

ModelType = TypeVar("ModelType", bound=models.Model)
OutSchemaType = TypeVar("OutSchemaType", bound=PydanticBaseModel)


class BaseOutSchema(PydanticBaseModel):
    id: uuid.UUID

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

    async def aupdate(self, data: Union[PydanticBaseModel, dict]) -> ModelType:
        if isinstance(data, PydanticBaseModel):
            data = data.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(self, field, value)

        await self.asave()
        await self.arefresh_from_db()
        return self


class BaseService(Generic[ModelType, OutSchemaType]):
    def __init__(self, manager: Type[ModelType], out_schema: Type[OutSchemaType]):
        self.repo = manager
        self.out_schema = out_schema

    def to_domain(self, obj) -> OutSchemaType:
        """Convert Django model instance to Pydantic schema."""
        return self.out_schema.model_validate(obj)

    async def evaluate_queryset(self, queryset, skip: int = 0, limit: int = 100) -> List[OutSchemaType]:
        """Paginate and convert from Django model instance to Pydantic schema."""
        result = await sync_to_async(list)(queryset.filter(cursor__gt=skip)[:limit])
        return [self.to_domain(_) for _ in result]


