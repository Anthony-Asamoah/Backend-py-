from django.contrib.postgres.search import SearchVector
from django.core.files.base import ContentFile

from auth.models import UserAccount
from main.utils.base_classes import BaseRepository, ModelType
from main.utils.logger import log
from media.models import Media
from media.schema import MediaRepoCreate


class MediaRepository(BaseRepository):

    async def create(self, payload: MediaRepoCreate) -> ModelType:
        # Convert FastAPI UploadFile to Django File
        file_content = await payload.file.read()
        payload.file = ContentFile(file_content, name=payload.file.filename)
        return await self.model.objects.acreate(**payload.model_dump())

    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
    ) -> list[UserAccount]:
        log.debug(f'init list user accounts with skip: {skip}, limit: {limit}')

        query = self.model.objects

        search_fields = ['title', 'description']
        if search:
            results = query.annotate(search=SearchVector(*search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        query = self.model.objects.all()
        result = await self.paginate_queryset(query, skip, limit)
        return result


media_repo = MediaRepository(Media)
