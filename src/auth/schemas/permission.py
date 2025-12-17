from typing import Optional

from pydantic import BaseModel

from main.utils.base_classes import BaseOutSchema


class PermissionBase(BaseModel):
    name: str

    class Config:
        from_attributes = True
        exclude_unset = True


class PermissionRepoCreate(PermissionBase):
    pass


class PermissionOut(BaseOutSchema, PermissionBase):
    pass


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    name: Optional[str] = None
