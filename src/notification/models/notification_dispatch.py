from django.db import models

from main.utils.base_classes import BaseModel
from notification.schemas.notification_dispatch import NotificationStatus, NotificationChannel


class NotificationDispatch(BaseModel):
    notification = models.ForeignKey(
        'notification.Notification',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches'
    )
    user = models.ForeignKey(
        'user_info.UserInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_dispatches'
    )

    subject = models.CharField(max_length=255, blank=True, null=True)
    heading = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    links = models.JSONField(default=list, blank=True, null=True)  # format: [{"label": <str>, "url": <str>}]

    channel = models.CharField(
        max_length=50,
        choices=NotificationChannel.choices
    )
    status = models.CharField(
        max_length=50,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )

    sent_on = models.DateTimeField(blank=True, null=True)
    delivered_on = models.DateTimeField(blank=True, null=True)
    read_on = models.DateTimeField(blank=True, null=True)

    error_message = models.TextField(blank=True, null=True)
    extra_info = models.JSONField(default=dict, blank=True, null=True)  # Additional metadata

    class Meta:
        db_table = 'notification_dispatches'
        ordering = ['cursor']

    def __str__(self):
        return f"{self.get_channel_display()} dispatch for {self.user}"
