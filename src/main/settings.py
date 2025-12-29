import logging
from email.policy import default
from os import path
from pathlib import Path

from decouple import Csv, Config, RepositoryEnv
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext

BASE_DIR = Path(__file__).resolve().parent.parent

DOTENV_FILE = BASE_DIR.parent / '.env'
config = Config(RepositoryEnv(DOTENV_FILE))

DATABASES = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': config('DB_HOST', cast=str),
        'USER': config('DB_USER', cast=str),
        'PASSWORD': config('DB_PASSWORD', cast=str),
        'NAME': config('DB_NAME', cast=str),
        'PORT': config('DB_PORT', cast=int),
    }
}

DEBUG = config('DEBUG', cast=bool, default=False)
SECRET_KEY = config('SECRET_KEY', cast=str)
LOG_LEVEL = config('LOG_LEVEL', cast=int, default=logging.INFO)

APP_TITLE = config('APP_TITLE', cast=str, default='Web Application')
APP_DESCRIPTION = config('APP_DESCRIPTION', cast=str, default='')
APP_VERSION = config('APP_VERSION', cast=str, default='0.0.1')

APP_HOST = config('APP_HOST', cast=str)
APP_PORT = config('APP_PORT', cast=int)
APP_RELOAD = config('APP_RELOAD', cast=bool, default=False)
API_PREFIX = config('API_PREFIX', cast=str, default='/api/v1')
DOCS_URL = config('DOCS_URL', cast=str, default='/docs')
AUTH_SECURITY_SCHEME = HTTPBearer(
    scheme_name="Bearer Token",
    description="Place your JWT access token here",
)

PWD_CONTEXT = CryptContext(schemes=["argon2"], deprecated="auto")

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'auth',
    'media',
    'user_info',
    'notification',
]

# Seeding and data
ADMIN_EMAIL = config('ADMIN_EMAIL', cast=str, default='')
ADMIN_PHONE = config('ADMIN_PHONE', cast=str, default='')
ADMIN_PASSWORD = config('ADMIN_PASSWORD', cast=str, default='')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')

# Throttling
RATE_LIMIT = config('RATE_LIMIT', cast=int, default=10)  # Max 10 requests
TIME_WINDOW = config('TIME_WINDOW', cast=int, default=3)  # Per 3 seconds

# Auth & JWT
AUTH_USER_MODEL = 'auth.UserAccount'
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = config('PASSWORD_RESET_TOKEN_EXPIRE_HOURS', cast=int, default=24)
ACCESS_TOKEN_EXPIRES_IN_MINUTES = config('ACCESS_TOKEN_EXPIRES_IN_MINUTES', cast=int, default=60)
REFRESH_TOKEN_EXPIRES_IN_MINUTES = config('REFRESH_TOKEN_EXPIRES_IN_MINUTES', cast=int, default=60 * 24)
ALGORITHM: str = "HS256"
JWT_SECRET_KEY: str = config('JWT_SECRET_KEY', cast=str, default='secret')
JWT_PRIVATE_KEY: str = config('JWT_PRIVATE_KEY', cast=str, default='private_secret')
JWT_PUBLIC_KEY: str = config('JWT_PUBLIC_KEY', cast=str, default='public_secret')
JWT_REFRESH_KEY: str = config('JWT_REFRESH_KEY', cast=str, default='refresh_secret')

# Cache Configuration
CACHE_SERVICE = config('CACHE_SERVICE', cast=str, default='inmem')  # 'inmem' or 'redis'
DEFAULT_CACHE_STORES = [
    'revoked_token'
]
# Redis Configuration (only used if CACHE_SERVICE='redis')
REDIS_HOST = config('REDIS_HOST', cast=str, default='localhost')
REDIS_PORT = config('REDIS_PORT', cast=int, default=6379)
REDIS_DB = config('REDIS_DB', cast=int, default=0)
REDIS_PASSWORD = config('REDIS_PASSWORD', cast=str, default='')
REDIS_MAX_CONNECTIONS = config('REDIS_MAX_CONNECTIONS', cast=int, default=10)
REDIS_SOCKET_TIMEOUT = config('REDIS_SOCKET_TIMEOUT', cast=int, default=5)
REDIS_CONNECT_TIMEOUT = config('REDIS_CONNECT_TIMEOUT', cast=int, default=5)

# STORAGE
STORAGE_TYPE = config('STORAGE_BACKEND', cast=str, default='LOCAL').upper()

# Local Storage
MEDIA_URL = 'media/uploads/'
MEDIA_ROOT = path.join(BASE_DIR, MEDIA_URL)
UPLOAD_ROOT = path.join(BASE_DIR, MEDIA_URL).replace('\\', '/')

STORAGES = {
    "default": {"BACKEND": 'django.core.files.storage.FileSystemStorage'},
}
MEDIA_PROCESSOR_TYPE = config('MEDIA_PROCESSOR_TYPE', cast=str, default='LOCAL').upper()
CLOUD_STORAGE_FOLDER_NAME = config("CLOUD_STORAGE_FOLDER_NAME", default=APP_TITLE)
CLOUD_MEDIA_PROCESSOR_URL = config('CLOUD_MEDIA_PROCESSOR_URL', cast=str, default='')

GS_CUSTOM_ENDPOINT = config('GS_FILE_PREVIEW_URL', cast=str, default='')
AWS_CUSTOM_ENDPOINT = config('AWS_FILE_PREVIEW_URL', cast=str, default='')

if STORAGE_TYPE == 'S3':
    # AWS S3 Storage settings
    STORAGES['default']['BACKEND'] = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', cast=str)
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', cast=str)
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', cast=str)
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', cast=str)
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', cast=str)
    AWS_SIGNED_URL_EXPIRATION = config("AWS_SIGNED_URL_EXPIRATION", cast=int, default=3600)
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_QUERYSTRING_AUTH = config('USE_SIGNED_URL', cast=bool, default=False)  # Set to True to use signed urls
    STATIC_URL = AWS_CUSTOM_ENDPOINT

elif STORAGE_TYPE == 'GCP':
    # Google Cloud Storage settings
    STORAGES['default']['BACKEND'] = 'storages.backends.gcloud.GoogleCloudStorage'

    GS_PROJECT_ID = config('GCP_PROJECT_ID', cast=str)
    GS_BUCKET_NAME = config('GCP_BUCKET_NAME', cast=str)
    GCP_CREDENTIALS_FILE = config('GCP_CREDENTIALS_FILE', cast=str, default='gcp_service_account.json')
    GS_QUERYSTRING_AUTH = config('USE_SIGNED_URL', cast=bool, default=False)  # Set to True to use signed urls

    # Static Files
    STATIC_URL = GS_CUSTOM_ENDPOINT

    # Google Cloud Tasks Configuration
    GCP_LOCATION = config('GCP_LOCATION', default='us-central1')
    GCP_QUEUE_NAME = config('GCP_QUEUE_NAME', default='thumbnail-queue')

    from google.oauth2 import service_account

    try:
        GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
            BASE_DIR / GCP_CREDENTIALS_FILE
        )
    except:
        GS_CREDENTIALS = None
        logging.warning("GS credential file ignored")

# Thumbnail settings
THUMBNAIL_SIZES = {
    'small': (150, 150),
    'medium': (300, 300),
    'large': (600, 600),
}
IMAGE_QUALITY_IN_BYTES = config('IMAGE_QUALITY_LIMIT_IN_BYTES', cast=int, default=1000000)
FILE_SIZE_LIMIT_MB = config('MAX_FILE_SIZE', cast=int, default=50)
FILE_SIZE_LIMIT = FILE_SIZE_LIMIT_MB * 1024 * 1024

file_extension_mappings = {
    '.avif': 'image/avif',
    '.gif': 'image/gif',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',

    '.mp4': 'video/mp4',
    '.webm': 'video/webm',

    '.mp3': 'audio/mpeg',

    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',

    '.txt': 'text/plain',
}
ALLOWED_MIME_TYPES = file_extension_mappings.values()

# Notification
EMAIL_TEMPLATE_DIR: str = str(BASE_DIR / 'notification' / 'channels' / 'email' / 'templates')
MAIL_SERVER: str = config('MAIL_SERVER', cast=str, default='')
MAIL_PORT: int = config('MAIL_PORT', cast=int, default='')
MAIL_USERNAME: str = config('MAIL_USERNAME', cast=str, default='')
MAIL_PASSWORD: str = config('MAIL_PASSWORD', cast=str, default='')
MAIL_FROM: str = config('MAIL_FROM', cast=str, default='')
MAIL_USE_TLS: bool = config('MAIL_USE_TLS', cast=bool, default='')

SMTP_RECIPIENTS_LIMIT: int = config('SMTP_RECIPIENTS_LIMIT', cast=int, default=100)
SMS_IS_DEBUG: bool = config('SMS_IS_DEBUG', cast=bool, default=False)
SMS_SENDER_NAME: str = APP_TITLE
SMS_PROVIDER: str = 'ARKESEL'

ARKESEL_BASE_URL: str = config('ARKESEL_BASE_URL', cast=str, default='https://sms.arkesel.com/api/v2')
ARKESEL_SENDER_CHAR_LIMIT: int = 11
ARKESEL_API_KEY: str = config('ARKESEL_API_KEY', cast=str, default='')
