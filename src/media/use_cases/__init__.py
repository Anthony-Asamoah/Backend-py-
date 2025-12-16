from typing import Annotated, Optional

from fastapi import Depends, BackgroundTasks, UploadFile, Request
from fastapi.params import Form

from auth.schema import UserAccountOut
from auth.utils import get_current_user
from main.utils.base_classes import BaseService
from media.schema import MediaOut, MediaCreate
from .create_media import create_media
from .delete_media import delete_media
from .download_media import download_media
from .get_media import get_media
from .list_media import list_media
from .stream_media import stream_media
from ..repositories import media_repo


class MediaService(BaseService):

    async def upload(
            self,
            file: UploadFile,
            title: Optional[str] = Form(None),
            description: Optional[str] = Form(None),
            is_reusable: bool = Form(False),
            language: Optional[str] = Form(None),
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
            tasks: BackgroundTasks = None
    ):
        """Upload a file"""
        return await create_media(self, MediaCreate(
            file=file,
            title=title,
            description=description,
            is_reusable=is_reusable,
            language=language,
        ), current_user, tasks)

    async def stream(
            self,
            id: str,
            request: Request,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Stream media by ID with range support for video/audio seeking."""
        return await stream_media(self, id, request)

    async def download(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Download media by ID."""
        return await download_media(self, id)

    async def read(
            self,
            search: str = None,
            id: str = None,
            skip: int = 0,
            limit: int = 100,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> list:
        """Get a paginated list of media."""
        return await list_media(self, search, id, skip, limit)

    async def delete(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ) -> None:
        """Delete by ID."""
        return await delete_media(self, id)

    async def get(
            self,
            id: str,
            current_user: Annotated[UserAccountOut, Depends(get_current_user)] = None,
    ):
        """Get media by ID."""
        return await get_media(self, id)


media_service = MediaService(
    repository=media_repo,
    out_schema=MediaOut
)
