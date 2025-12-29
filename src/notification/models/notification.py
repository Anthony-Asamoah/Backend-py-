import pendulum
from django.db import models

from main.utils.base_classes import BaseModel


class Notification(BaseModel):
    template = models.ForeignKey(
        'notification.NotificationTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    user_info = models.ForeignKey(
        'user_info.UserInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    @property
    async def status(self):
        from notification.utils import get_status
        return await get_status(self.dispatches)

    @property
    async def channels(self):
        from notification.utils import get_channels
        return await get_channels(self.dispatches)

    @property
    def elapsed_time(self) -> str:
        """Time elapsed since notification creation."""
        time_from_creation = pendulum.now() - pendulum.instance(self.created_on)
        msg = time_from_creation.in_words()
        return msg

    class Meta:
        db_table = 'notifications'
        ordering = ['cursor']

    def __str__(self):
        return f"Notification {self.id} for {self.user_info}"
