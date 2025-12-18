from typing import List

from fastapi import Depends

from auth.utils.rbac import check_user_permission
from main.utils.exception_handling import SafeAPIRouter
from media.schemas import MediaOut
from media.use_cases import media_service

media_router = SafeAPIRouter()

media_router.get(
    '/{id}/stream',
    response_model=None,  # Returns StreamingResponse or RedirectResponse
    status_code=200,
    dependencies=[Depends(check_user_permission(['media.media:read', 'media.*:*']))],
    summary="Stream media file by ID",
)(media_service.stream)

media_router.get(
    '/{id}/download',
    response_model=None,  # Returns FileResponse or RedirectResponse
    status_code=200,
    dependencies=[Depends(check_user_permission(['media.media:read', 'media.*:*']))],
    summary="Download media file by ID",
)(media_service.download)

media_router.post(
    '',
    response_model=MediaOut,
    status_code=201,
    dependencies=[Depends(check_user_permission(['media.media:create', 'media.*:*']))],
    summary="Upload a new media file",
)(media_service.upload)

media_router.get(
    '',
    response_model=List[MediaOut],
    status_code=200,
    dependencies=[Depends(check_user_permission(['media.media:read', 'media.*:*']))],
    summary="List all media files",
)(media_service.read)

media_router.delete(
    '/{id}',
    status_code=204,
    dependencies=[Depends(check_user_permission(['media.media:delete', 'media.*:*']))],
    summary="Delete media file by ID",
)(media_service.delete)
