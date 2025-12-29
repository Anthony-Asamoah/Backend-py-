from typing import Optional

from pydantic import BaseModel

from main.utils.base_classes import BaseOutSchema


class NotificationTemplateBase(BaseModel):
    name: str
    subject: str
    heading: str
    email_content: str
    short_content: str


class NotificationTemplateRepoCreate(NotificationTemplateBase):
    pass


class NotificationTemplateOut(BaseOutSchema, NotificationTemplateBase):
    pass


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(NotificationTemplateBase):
    name: Optional[str] = None
    subject: Optional[str] = None
    heading: Optional[str] = None
    email_content: Optional[str] = None
    short_content: Optional[str] = None
