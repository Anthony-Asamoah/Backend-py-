import os

import django

from main.middleware.throttling import RateLimitMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from main import settings
from main.router import app_router
from main.lifespan import life_span

# get django app
application = get_asgi_application()

# init fastapi app
server = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}{settings.DOCS_URL}",
    debug=settings.DEBUG,
    lifespan=life_span
)

# bind django to fastapi
server.mount("/django", application)
server.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

# add middleware
server.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
server.add_middleware(RateLimitMiddleware)

# import router
server.include_router(app_router)
