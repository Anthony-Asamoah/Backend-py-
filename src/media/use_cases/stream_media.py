from pathlib import Path
from typing import Generator

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import UUID4

from main.utils.logger import log


async def stream_media(cls, id: UUID4, request: Request):
    """Stream a media file with support for range requests (seeking in video/audio)"""
    log.debug(f'init stream media with id: {id}')

    media = await cls.repo.get_by_id(id)
    if not media: raise HTTPException(
        status_code=404, detail="Media not found"
    )
    if not media.file: raise HTTPException(
        status_code=404, detail="File not found"
    )

    match media.storage_backend:
        case "LOCAL":
            # For local storage, stream with range support
            file_path = Path(media.file.path)
            if not file_path.exists(): raise HTTPException(
                status_code=404, detail="File not found in local storage"
            )

            file_size = file_path.stat().st_size
            range_header = request.headers.get("range")

            # Handle range requests for seeking
            if range_header:
                range_start, range_end = _parse_range_header(range_header, file_size)
                content_length = range_end - range_start + 1

                def file_iterator(start: int, end: int) -> Generator[bytes, None, None]:
                    with open(file_path, "rb") as f:
                        f.seek(start)
                        remaining = end - start + 1
                        while remaining > 0:
                            chunk_size = min(8192, remaining)
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk

                return StreamingResponse(
                    file_iterator(range_start, range_end),
                    status_code=206,  # Partial Content
                    headers={
                        "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(content_length),
                        "Content-Type": media.mime_type or "application/octet-stream",
                    })
            else:
                # No range header, stream entire file
                def file_iterator() -> Generator[bytes, None, None]:
                    with open(file_path, "rb") as f:
                        while chunk := f.read(8192):
                            yield chunk

                return StreamingResponse(
                    file_iterator(),
                    status_code=200,
                    headers={
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(file_size),
                        "Content-Type": media.mime_type or "application/octet-stream",
                    },
                )

        case "AWS":
            # For S3, redirect to the URL (S3 handles streaming)
            file_url = media.file.url
            return RedirectResponse(url=file_url, status_code=302)

        case "GCP":
            # For GCS, redirect to the URL (GCS handles streaming)
            file_url = media.file.url
            return RedirectResponse(url=file_url, status_code=302)

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported storage backend: {media.storage_backend}"
            )


def _parse_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    """Parse Range header and return start and end bytes"""
    try:
        range_str = range_header.replace("bytes=", "")
        range_start, range_end = range_str.split("-")

        start = int(range_start) if range_start else 0
        end = int(range_end) if range_end else file_size - 1

        # Validate range
        if start >= file_size or end >= file_size or start > end:
            raise ValueError("Invalid range")

        return start, end
    except (ValueError, AttributeError):
        raise HTTPException(status_code=416, detail="Invalid range header")
