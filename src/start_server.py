from uvicorn import run

from main import settings

if __name__ == "__main__":
    run(
        "main.asgi:server",
        reload=settings.APP_RELOAD,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )
