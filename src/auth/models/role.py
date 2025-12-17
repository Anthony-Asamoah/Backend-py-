from django.db import models

from main.utils.base_classes import BaseModel


class Role(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    default = models.BooleanField(default=False)
    users = models.ManyToManyField("auth.UserAccount", related_name='roles')
    permissions = models.ManyToManyField("auth.Permission", related_name='roles')

    def __str__(self):
        return self.name
