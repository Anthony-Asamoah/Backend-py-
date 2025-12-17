import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import UUID4

from main.utils.logger import log


async def download_media(cls, id: UUID4):
    """Download a media file - returns FileResponse for local, redirects for cloud storage"""
    log.debug(f'init download media with id: {id}')

    media = await cls.repo.get_by_id(id)
    if not media: raise HTTPException(
        status_code=404, detail="Media not found"
    )
    if not media.file: raise HTTPException(
        status_code=404, detail="File not found"
    )

    # Get the filename from the file path
    filename = os.path.basename(media.file.name)

    match media.storage_backend:
        case "LOCAL":
            # For local storage, serve the file directly
            file_path = Path(media.file.path)
            if not file_path.exists():
                raise HTTPException(
                    status_code=404, detail="File not found in local storage"
                )
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type=media.mime_type or 'application/octet-stream'
            )

        case "AWS":
            # For S3, redirect to the signed URL
            file_url = media.file.url
            return RedirectResponse(
                url=file_url,
                status_code=302
            )

        case "GCP":
            # For GCS, redirect to the public URL
            file_url = media.file.url
            return RedirectResponse(
                url=file_url,
                status_code=302
            )

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported storage backend: {media.storage_backend}"
            )
