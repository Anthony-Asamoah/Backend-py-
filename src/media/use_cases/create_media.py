from typing import Optional

from fastapi import BackgroundTasks

from auth.schema import UserAccountOut
from main import settings
from main.utils.logger import log
from media.schema import MediaCreate, MediaOut, MediaRepoCreate
from media.utils import get_file_mime_type, get_media_metadata


async def create_media(
        cls,
        payload: MediaCreate,
        current_user: Optional[UserAccountOut] = None,
        background_worker: Optional[BackgroundTasks] = None,
) -> MediaOut:
    log.debug(f'init new media with payload: {payload} & file: {payload.file.filename}')

    file = payload.file

    # populate all fields
    if not payload.title: payload.title = file.filename
    payload.storage_backend = settings.STORAGE_TYPE

    payload.file_size = file.size

    mime_type = get_file_mime_type(file)
    payload.mime_type = mime_type

    payload = await get_media_metadata(payload, payload.file)

    # Create the media instance and save the file
    new_media = await cls.repo.create(MediaRepoCreate(
        **payload.model_dump(),
        uploaded_by_id=current_user.cursor
    ))

    # background_worker.add_task(upload_file)
    # background_worker.add_task(generate_thumbnails)

    return await cls.to_domain(new_media)
