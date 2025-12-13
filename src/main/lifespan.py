from contextlib import asynccontextmanager

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from fastapi import FastAPI

from main.utils.dependency_injection import VarContainer
from main.utils.logger import log

# init schedular & it's registry
scheduler = BackgroundScheduler()
from main.jobs import scheduled_jobs

singletons = VarContainer()


@asynccontextmanager
async def life_span(app: FastAPI):
    log.info(f"Booting @{timezone.now().time().isoformat()}")

    scheduler.start()
    for func, args, kwargs in scheduled_jobs.unpack():
        scheduler.add_job(func, *args, **kwargs)

    singletons.register(httpx.AsyncClient(timeout=5), name='http_client')

    yield
    log.info(f"Shutting down @{timezone.now().time().isoformat()}")
    scheduler.shutdown()
