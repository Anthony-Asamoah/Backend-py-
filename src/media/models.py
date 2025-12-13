from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from main.utils.base_classes import BaseModel
from media.utils import get_preview_url, media_upload_path

User = get_user_model()


class StorageBackend(models.TextChoices):
    LOCAL = 'LOCAL'
    AWS = 'AWS'
    GCP = 'GCP'


class Media(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=media_upload_path)
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # For video/audio
    language = models.CharField(max_length=100, null=True, blank=True)

    # Thumbnail fields
    thumbnail_small = models.ImageField(upload_to='thumbnails/small/', blank=True, null=True)
    thumbnail_medium = models.ImageField(upload_to='thumbnails/medium/', blank=True, null=True)
    thumbnail_large = models.ImageField(upload_to='thumbnails/large/', blank=True, null=True)
    thumbnails_generated = models.BooleanField(default=False, db_default=False)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_reusable = models.BooleanField(default=True, db_default=False)

    storage_backend = models.CharField(
        max_length=20,
        choices=StorageBackend.choices,
        default=StorageBackend.LOCAL.name
    )

    class Meta:
        db_table = 'media'
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    @property
    def preview_url(self):
        return get_preview_url(self)

    @property
    def file_url(self):
        if self.file: return self.file.url
        return None

    def get_thumbnail_url(self, size='medium'):
        thumbnail_field = getattr(self, f'thumbnail_{size}', None)
        if thumbnail_field and thumbnail_field.name and self.storage_backend != 'LOCAL':
            return f"{settings.GS_CUSTOM_ENDPOINT}{thumbnail_field.name}"
        return self.preview_url


class GenericMediaRelation(BaseModel):
    media = models.OneToOneField('media.Media', on_delete=models.CASCADE)
    label = models.CharField(max_length=300, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    sorting = models.IntegerField(default=0, db_default=0)

    class Meta:
        ordering = ['sorting']
        abstract = True

    def __str__(self):
        return self.label or super().__str__()
