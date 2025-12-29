from datetime import datetime
from typing import Optional, Any, Dict, List

from django.db import models
from pydantic import BaseModel
from pydantic import UUID4

from main.utils.base_classes import BaseOutSchema


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    DELIVERED = "DELIVERED", "Delivered"
    READ = "READ", "Read"


class NotificationChannel(models.TextChoices):
    SMS = "SMS", "SMS"
    EMAIL = "EMAIL", "Email"
    WEBSOCKET = "WEBSOCKET", "Websocket"


class DispatchLinkSchema(BaseModel):
    label: str
    url: str


class NotificationDispatchBase(BaseModel):
    user_id: UUID4 | int
    content: str
    channel: NotificationChannel
    subject: Optional[str] = None
    heading: Optional[str] = None
    links: Optional[List[DispatchLinkSchema]] = None
    error_message: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None


class NotificationDispatchRepoCreate(NotificationDispatchBase):
    notification_id: Optional[int] = None
    user_id: int


class NotificationDispatchCreate(NotificationDispatchBase):
    notification_id: UUID4
    context: Optional[Dict[str, Any]] = None
    links: Optional[List[DispatchLinkSchema]] = None


class NotificationDispatchOut(BaseOutSchema, NotificationDispatchBase):
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None
    status: Optional[str] = None
    sent_on: Optional[datetime] = None
    delivered_on: Optional[datetime] = None
    read_on: Optional[datetime] = None
