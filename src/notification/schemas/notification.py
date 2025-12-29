from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, UUID4

from main.utils.base_classes import BaseOutSchema
from notification.schemas.notification_dispatch import NotificationStatus, NotificationChannel
from user_info.schemas import UserInfoOut


class NotificationBase(BaseModel):
    template_id: Optional[int]
    user_info_id: Optional[int]


class NotificationRepoCreate(NotificationBase):
    pass


class NotificationOut(BaseOutSchema, NotificationBase):
    status: Optional[NotificationStatus] = None
    channels: Optional[List[NotificationChannel]] = None
    elapsed_time: Optional[str] = None
    dispatches: Optional[List["RelatedDispatchSchema"]] = []
    user_info: Optional[UserInfoOut] = None


class NotificationCreate(BaseModel):
    template_name: str
    context: Optional[Dict[str, Any]] = None
    channels: Optional[List[NotificationChannel]] = [
        NotificationChannel.EMAIL,
        NotificationChannel.SMS,
        NotificationChannel.WEBSOCKET,
    ]
    links: Optional[List["DispatchLinkSchema"]] = None


class NotificationSendResult(BaseModel):
    is_success: Optional[bool] = None
    message: Optional[str] = None


class RelatedDispatchSchema(BaseModel):
    id: Optional[UUID4] = None
    channel: Optional[NotificationChannel] = None
    status: Optional[str] = None

    sent_on: Optional[datetime] = None
    delivered_on: Optional[datetime] = None
    read_on: Optional[datetime] = None

    error_message: Optional[str] = None
    extra_info: Optional[Any] = None

    class Config:
        from_attributes = True


class DispatchLinkSchema(BaseModel):
    label: str
    url: str
