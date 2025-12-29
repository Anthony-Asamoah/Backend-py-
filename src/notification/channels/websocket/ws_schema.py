from typing import Any

from pydantic import BaseModel

response_config = dict(
    exclude_none=True,
)


class WsResponse(BaseModel):
    is_success: bool = True
    error: str = None
    count: int = None
    detail: dict[str, Any] = None

    @staticmethod
    def fail(message: str = "An error occurred") -> dict[str, Any]:
        response = WsResponse(
            error=message,
            is_success=False,
        )
        return response.model_dump(**response_config)

    @staticmethod
    def success(count: int = None) -> dict[str, Any]:
        response = WsResponse(count=count)
        return response.model_dump(**response_config)

    @staticmethod
    def data(**payload: dict) -> dict[str, Any]:
        response = WsResponse(detail=payload)
        return response.model_dump(**response_config)
