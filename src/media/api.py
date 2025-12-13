from typing import List

from main.utils.exception_handling import SafeAPIRouter
from media.schema import MediaOut
from media.use_cases import media_service

media_router = SafeAPIRouter()

media_router.get(
    '/{id}/stream',
    response_model=None,  # Returns StreamingResponse or RedirectResponse
    status_code=200,
)(media_service.stream)

media_router.get(
    '/{id}/download',
    response_model=None,  # Returns FileResponse or RedirectResponse
    status_code=200,
)(media_service.download)

media_router.post(
    '',
    response_model=MediaOut,
    status_code=201,
)(media_service.upload)  # Changed from .create to .upload

media_router.get(
    '',
    response_model=List[MediaOut],
    status_code=200,
)(media_service.read)

media_router.delete(
    '/{id}',
    status_code=204,
)(media_service.delete)
