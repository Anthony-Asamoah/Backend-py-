from pydantic import UUID4

from main.utils.logger import log
from media.utils import delete_file_by_path


async def delete_media(cls, id: UUID4) -> None:
    """Delete media record and associated files from storage"""
    log.debug(f'init delete media {id}')

    media = await cls.get(id)
    # Delete the main file
    if media.file_url:
        try:
            await delete_file_by_path(media.file_url, media.storage_backend)
        except Exception as e:
            log.warning(f'Failed to delete main file: {e}')

    # Delete thumbnails if they exist
    for size in ['small', 'medium', 'large']:
        thumbnail_field = getattr(media, f'thumbnail_{size}', None)
        if thumbnail_field and thumbnail_field.name:
            try:
                await delete_file_by_path(thumbnail_field.name, media.storage_backend)
            except Exception as e:
                log.warning(f'Failed to delete {size} thumbnail: {e}')

    # Delete the database record
    await cls.repo.delete(id)
    log.info(f'Deleted media {id} and associated files')
