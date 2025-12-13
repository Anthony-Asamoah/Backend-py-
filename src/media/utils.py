import io
import mimetypes
import os
import tempfile
import uuid
from io import BytesIO

import pillow_avif  # noqa
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from fastapi import UploadFile
from moviepy import VideoFileClip, AudioFileClip
from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.s3boto3 import S3Boto3Storage

from main.settings import IMAGE_QUALITY_IN_BYTES, file_extension_mappings
from main.utils.logger import log


def media_upload_path(instance, filename):
    parts = filename.split('.')
    ext = parts[-1]
    name = ''.join(parts[:-1])

    # Derive media type from mime_type if available
    media_type = 'files'  # default
    if hasattr(instance, 'mime_type') and instance.mime_type:
        if instance.mime_type.startswith('image'):
            media_type = 'images'
        elif instance.mime_type.startswith('video'):
            media_type = 'videos'
        elif instance.mime_type.startswith('audio'):
            media_type = 'audio'
        elif instance.mime_type.startswith('application'):
            media_type = 'documents'

    # Clean up title if it ends with /
    title_prefix = ''
    if instance.title and not instance.title.endswith('/'):
        title_prefix = instance.title + '/'
    elif instance.title:
        title_prefix = instance.title

    filename = f"{title_prefix}{name}-{str(uuid.uuid4())[-6:]}.{ext}"
    return os.path.join(media_type, filename)


def get_storage_backend(backend_type=None):
    """Get the appropriate storage backend"""
    if not backend_type:
        backend_type = settings.STORAGE_BACKEND

    if backend_type == 'AWS':
        return S3Boto3Storage()
    elif backend_type == 'GCP':
        return GoogleCloudStorage()
    else:
        return default_storage


async def delete_file_from_local(path: str):
    """Delete a file from local storage"""
    from asgiref.sync import sync_to_async

    try:
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            await sync_to_async(os.remove)(file_path)
            log.info(f'Deleted local file: {file_path}')
        else:
            log.warning(f'Local file not found: {file_path}')
    except Exception as e:
        log.error(f'Failed to delete local file {path}: {e}')
        raise


async def delete_file_from_s3(path: str):
    """Delete a file from AWS S3 storage"""
    from asgiref.sync import sync_to_async

    try:
        storage = S3Boto3Storage()
        await sync_to_async(storage.delete)(path)
        log.info(f'Deleted S3 file: {path}')
    except Exception as e:
        log.error(f'Failed to delete S3 file {path}: {e}')
        raise


async def delete_file_from_gcs(path: str):
    """Delete a file from Google Cloud Storage"""
    from asgiref.sync import sync_to_async

    try:
        storage = GoogleCloudStorage()
        await sync_to_async(storage.delete)(path)
        log.info(f'Deleted GCS file: {path}')
    except Exception as e:
        log.error(f'Failed to delete GCS file {path}: {e}')
        raise


async def delete_file_by_path(path: str, storage_type: str = None):
    """Delete a file from storage based on storage type"""
    if storage_type is None: storage_type = settings.STORAGE_TYPE

    match storage_type.upper():
        case "LOCAL":
            await delete_file_from_local(path)
        case "AWS":
            await delete_file_from_s3(path)
        case "GCP":
            await delete_file_from_gcs(path)
        case _:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    return {"detail": "File deleted"}


def get_preview_url(media_instance):
    """Generate preview URL for different storage backends"""
    if media_instance.storage_backend == 'LOCAL':
        return f"{settings.BACKEND_URL}media/{media_instance.pk}/preview/"
    # elif media_instance.storage_backend == 'AWS':
    #     return f"{settings.AWS_CUSTOM_ENDPOINT}{media_instance.file.name}"
    # elif media_instance.storage_backend == 'GCP':
    #     return f"{settings.GS_CUSTOM_ENDPOINT}{media_instance.file.name}"
    return media_instance.file.url


def humanize_file_size(size_bytes: int) -> str:
    if not isinstance(size_bytes, (int, float)) or size_bytes < 0: return "0 B"

    # Define size units
    units = [
        (1024 ** 4, "TB"),
        (1024 ** 3, "GB"),
        (1024 ** 2, "MB"),
        (1024 ** 1, "KB"),
        (1, "B")
    ]

    for threshold, unit in units:
        if size_bytes >= threshold:
            size = size_bytes / threshold
            # Format with appropriate decimal places
            if size >= 100:
                return f"{size:.0f} {unit}"
            elif size >= 10:
                return f"{size:.1f} {unit}"
            else:
                return f"{size:.2f} {unit}"

    return f"{size_bytes} B"


def get_file_mime_type(file: UploadFile):
    mime_type = None

    # Try to get MIME type from file content type first
    if hasattr(file, 'content_type') and file.content_type:
        mime_type = file.content_type

    # Fallback to guessing from filename
    if not mime_type and hasattr(file, 'name') and file.name:
        mime_type, _ = mimetypes.guess_type(file.name)

    # If still no MIME type, try to guess from file extension
    if not mime_type:
        file_extension = None
        if hasattr(file, 'name') and file.name:
            _, file_extension = os.path.splitext(file.name.lower())

        if file_extension in file_extension_mappings:
            mime_type = file_extension_mappings[file_extension]

    # Default MIME type if we couldn't determine it
    if not mime_type: mime_type = 'application/octet-stream'

    return mime_type


def validate_file(file):
    """Validate file type and size"""
    if not file: raise ValidationError("File is required")

    mime_type = get_file_mime_type(file)

    if mime_type not in settings.ALLOWED_MIME_TYPES: raise ValidationError(
        f"File type '{mime_type}' not allowed."
    )

    max_size = settings.FILE_SIZE_LIMIT
    if file.size > max_size: raise ValidationError(
        f"File too large. Maximum size: {humanize_file_size(max_size)}"
    )
    return file


def compress(image):
    im = Image.open(image)

    # Convert to RGB for consistent processing
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')

    im_io = BytesIO()
    file_size = image.size

    if file_size > IMAGE_QUALITY_IN_BYTES:
        # Calculate compression level (0-9, higher = more compression)
        compression_ratio = IMAGE_QUALITY_IN_BYTES / file_size
        compress_level = max(1, min(9, int(9 * (1 - compression_ratio))))
        im.save(im_io, 'PNG', optimize=True, compress_level=compress_level)
    else:
        im.save(im_io, 'PNG', optimize=True)

    # Update filename extension
    name_without_ext = os.path.splitext(image.name)[0]
    new_name = f"{name_without_ext}.png"

    new_image = File(im_io, name=new_name)
    return new_image


def generate_thumbnails(media_id):
    from .models import Media

    try:
        media = Media.objects.get(id=media_id)
        storage = get_storage_backend(media.storage_backend)

        # Derive media type from mime_type
        if media.mime_type and media.mime_type.startswith('image'):
            # Existing image logic
            if media.storage_backend == 'LOCAL':
                image_path = media.file.path
                with Image.open(image_path) as img:
                    generate_thumbnail_variants(media, img, storage)
            else:
                file_content = media.file.read()
                with Image.open(io.BytesIO(file_content)) as img:
                    generate_thumbnail_variants(media, img, storage)

        elif media.mime_type and media.mime_type.startswith('video'):
            # Video thumbnail generation
            if media.storage_backend == 'LOCAL':
                video_path = media.file.path
                generate_video_thumbnail(media, video_path, storage)
            else:
                # Download video to temporary file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    for chunk in media.file.chunks():
                        temp_file.write(chunk)
                    temp_file.flush()
                    temp_file_path = temp_file.name

                try:
                    generate_video_thumbnail(media, temp_file_path, storage)
                finally:
                    os.unlink(temp_file_path)
        else:
            return f"Skipping thumbnail generation for unsupported media type: {media.mime_type}"

        media.thumbnails_generated = True
        media.save()
        return f"Thumbnails generated successfully for media: {media_id}"

    except Media.DoesNotExist:
        return f"Media with ID {media_id} not found"
    except Exception as e:
        return f"Error generating thumbnails for media {media_id}: {str(e)}"


def generate_video_thumbnail(media, video_path, storage, timestamp=None):
    """Generate thumbnail from video at specified timestamp (defaults to middle of video)"""
    with VideoFileClip(video_path) as video:
        if timestamp is None: timestamp = video.duration / 100
        frame = video.get_frame(timestamp)

        # Convert numpy array to PIL Image
        img = Image.fromarray(frame.astype('uint8'))

    # Generate thumbnail variants using existing function
    generate_thumbnail_variants(media, img, storage)


def generate_thumbnail_variants(media, image, storage):
    """Generate thumbnail variants for different sizes"""
    for size_name, (width, height) in settings.THUMBNAIL_SIZES.items():
        # Create thumbnail
        img_copy = image.copy()
        img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)

        # Convert to RGB (PNG supports all modes)
        if img_copy.mode not in ('RGB', 'L'):
            img_copy = img_copy.convert('RGB')

        # Save thumbnail as PNG
        thumbnail_io = io.BytesIO()
        img_copy.save(thumbnail_io, format='PNG', optimize=True)
        file_ext = 'png'
        thumbnail_io.seek(0)

        # Generate filename
        original_name = os.path.splitext(os.path.basename(media.file.name))[0]
        thumbnail_filename = f"thumbnails/{size_name}/{original_name}_{size_name}.{file_ext}"

        # Save to storage
        if media.storage_backend == 'local':
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_filename)
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            with open(thumbnail_path, 'wb') as f:
                f.write(thumbnail_io.getvalue())
            thumbnail_url = f"/media/{thumbnail_filename}"
        else:
            # Save to cloud storage
            thumbnail_url = storage.save(thumbnail_filename, thumbnail_io)

        # Update media model
        setattr(media, f'thumbnail_{size_name}', thumbnail_url)


async def get_media_metadata(media_obj, file: UploadFile):
    if media_obj.mime_type.startswith('image'):
        try:
            # Read image to get dimensions
            file_content = await file.read()
            image = Image.open(BytesIO(file_content))
            media_obj.width, media_obj.height = image.size

            # Reset file pointer for later saving
            await file.seek(0)

        except Exception as e:
            log.warning(f'Failed to extract image dimensions: {e}')
            media_obj.width, media_obj.height = None, None

    elif media_obj.mime_type.startswith('video'):
        # Save to temporary file for video processing
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                file_content = await file.read()
                temp_file.write(file_content)
                temp_file.flush()
                temp_path = temp_file.name

            with VideoFileClip(temp_path) as video:
                media_obj.duration = video.duration
                media_obj.width, media_obj.height = video.size

            # Reset file pointer and clean up temp file
            await file.seek(0)
            os.unlink(temp_path)

        except Exception as e:
            log.warning(f'Failed to extract video metadata: {e}')
            media_obj.duration = None
            media_obj.width, media_obj.height = None, None

    elif media_obj.mime_type.startswith('audio'):
        # Save to temporary file for audio processing
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                file_content = await file.read()
                temp_file.write(file_content)
                temp_file.flush()
                temp_path = temp_file.name

            # Extract audio metadata
            with AudioFileClip(temp_path) as audio:
                media_obj.duration = audio.duration

            # Reset file pointer and clean up temp file
            await file.seek(0)
            os.unlink(temp_path)
        except Exception as e:
            log.warning(f'Failed to extract audio metadata: {e}')
            media_obj.duration = None

    return media_obj
