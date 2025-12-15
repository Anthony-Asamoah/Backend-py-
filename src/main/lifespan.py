from contextlib import asynccontextmanager

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from fastapi import FastAPI

from main.utils.cache import initialize_cache_service, shutdown_cache_service
from main.utils.dependency_injection import VarContainer
from main.utils.logger import log

# init schedular & it's registry
scheduler = BackgroundScheduler()
from main.jobs import scheduled_jobs

singletons = VarContainer()


@asynccontextmanager
async def life_span(app: FastAPI):
    log.info(f"Booting @{timezone.now().time().isoformat()}")

    # Initialize cache service
    cache = await initialize_cache_service()
    singletons.register(cache, name='cache')

    # initialize schedular & jobs
    scheduler.start()
    for func, args, kwargs in scheduled_jobs.unpack():
        scheduler.add_job(func, *args, **kwargs)

    # initialize http client
    singletons.register(httpx.AsyncClient(timeout=5), name='http_client')

    yield
    log.info(f"Shutting down @{timezone.now().time().isoformat()}")

    # Shutdown cache service
    cache = singletons.get('cache')
    await shutdown_cache_service(cache)

    # Close http client
    http_client = singletons.get('http_client')
    await http_client.aclose()

    scheduler.shutdown()
