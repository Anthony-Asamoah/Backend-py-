from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel

from main.utils.base_classes import BaseOutSchema


class ThumbNailOut(BaseModel):
    small: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None


class MediaBase(BaseModel):
    title: str
    description: Optional[str] = None
    storage_backend: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    language: Optional[str] = None
    is_reusable: bool = False
    thumbnails_generated: bool = False


class MediaRepoCreate(MediaBase):
    uploaded_by_id: int
    file: UploadFile


class MediaOut(BaseOutSchema, MediaBase):
    file_url: Optional[str] = None
    thumbnails: Optional[ThumbNailOut] = None


class MediaCreate(MediaBase):
    storage_backend: Optional[str] = None
    title: Optional[str] = None
    file: UploadFile
