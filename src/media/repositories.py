from django.core.files.base import ContentFile

from main.utils.base_classes import BaseRepository, ModelType
from media.models import Media
from media.schemas import MediaRepoCreate


class MediaRepository(BaseRepository):

    async def create(self, payload: MediaRepoCreate) -> ModelType:
        # Convert FastAPI UploadFile to Django File
        file_content = await payload.file.read()
        payload.file = ContentFile(file_content, name=payload.file.filename)
        return await self.model.objects.acreate(**payload.model_dump())


media_repo = MediaRepository(
    model=Media,
    search_fields=['title', 'description']
)
