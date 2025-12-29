from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from notification.models import NotificationDispatch
from user_info.models import UserInfo


@dataclass
class ProviderResponse:
    success: bool
    response: str
    message: Optional[str] = None


class NotificationProvider(ABC):
    """Base class for all notification channels"""

    @abstractmethod
    async def send(
            self,
            dispatch: NotificationDispatch,
            user_account: UserInfo,
    ) -> ProviderResponse:
        """Send notification through provider"""
        pass