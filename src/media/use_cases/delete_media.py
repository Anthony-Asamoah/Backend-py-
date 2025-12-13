from django.core.exceptions import ObjectDoesNotExist
from fastapi import HTTPException

from main.utils.logger import log
from media.utils import delete_file_by_path


async def delete_media(cls, id: str) -> None:
    """Delete media record and associated files from storage"""
    log.debug(f'init delete media {id}')

    try:
        media = await cls.repo.aget(id=id)

        # Delete the main file
        if media.file and media.file.name:
            try:
                await delete_file_by_path(media.file.name, media.storage_backend)
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
        await media.adelete()
        log.info(f'Deleted media {id} and associated files')

    except ObjectDoesNotExist:
        raise HTTPException(status_code=404, detail="Media not found")
