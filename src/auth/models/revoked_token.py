from django.db import models

from main.utils.base_classes import BaseModel


class RevokedToken(BaseModel):
    token = models.TextField(db_index=True, unique=True)
    expires_on = models.DateTimeField()
