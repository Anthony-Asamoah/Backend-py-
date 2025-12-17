from typing import Optional

from pydantic import BaseModel, UUID4

from auth.schemas.permission import PermissionOut
from main.utils.base_classes import BaseOutSchema


class RoleBase(BaseModel):
    name: str
    default: bool = False

    class Config:
        from_attributes = True
        exclude_unset = True


class RoleRepoCreate(RoleBase):
    pass


class RoleOut(BaseOutSchema, RoleBase):
    pass


class SingleRoleOut(BaseOutSchema, RoleBase):
    permissions: Optional[list[PermissionOut]] = None


class RoleCreate(RoleBase):
    permissions_ids: list[UUID4] = []
