from django.db import models

from main.utils.base_classes import BaseModel


class NotificationTemplate(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    heading = models.CharField(max_length=255, blank=True, null=True)
    email_content = models.TextField()
    short_content = models.TextField()  # For sms and push notifications

    class Meta:
        db_table = 'notification_templates'
        ordering = ['cursor']

    def __str__(self):
        return self.name
