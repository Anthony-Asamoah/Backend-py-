import inspect
from contextlib import contextmanager
from functools import wraps
from typing import Callable

from fastapi import APIRouter, HTTPException

from main.utils.logger import log


class SafeAPIRouter(APIRouter):
    """Custom APIRouter to raise 500 with an appropriate error message when an unexpected error occurs."""

    @contextmanager
    def _handle_exceptions(self):
        try:
            yield
        except HTTPException:
            raise
        except Exception:
            log.exception("The unexpected occurred")
            raise HTTPException(
                status_code=500,
                detail="Something went wrong. Kindly try again..."
            )

    def _wrap_with_exception_handler(self, func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self._handle_exceptions():
                    return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with self._handle_exceptions():
                return func(*args, **kwargs)

        return sync_wrapper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, path: str, **kwargs):
        """Override post method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).post(path, **kwargs)(wrapped_func)

        return decorator

    def get(self, path: str, **kwargs):
        """Override get method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).get(path, **kwargs)(wrapped_func)

        return decorator

    def put(self, path: str, **kwargs):
        """Override put method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).put(path, **kwargs)(wrapped_func)

        return decorator

    def patch(self, path: str, **kwargs):
        """Override patch method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).patch(path, **kwargs)(wrapped_func)

        return decorator

    def delete(self, path: str, **kwargs):
        """Override delete method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).delete(path, **kwargs)(wrapped_func)

        return decorator
