from django.db import models

from main.utils.base_classes import BaseModel


class Permission(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField("auth.UserAccount", related_name='permissions')

    def __str__(self):
        return self.name
