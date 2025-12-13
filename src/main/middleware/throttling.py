from time import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from main import settings

request_counts = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip in request_counts:
            request_times = request_counts[client_ip]

            # Remove outdated requests outside the time window
            request_counts[client_ip] = [
                timestamp for timestamp in request_times if current_time - timestamp < settings.TIME_WINDOW
            ]

            if len(request_counts[client_ip]) >= settings.RATE_LIMIT: return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"}
            )

        # Add current request timestamp
        request_counts.setdefault(client_ip, []).append(current_time)

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response
