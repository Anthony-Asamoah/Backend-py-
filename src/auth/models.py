from django.db import models

from auth.schema import IdentifierChoices, UserAccountStatusChoices
from main.utils.base_classes import BaseModel


class UserAccount(BaseModel):
    identifier = models.CharField(max_length=100)
    identifier_type = models.CharField(max_length=100, choices=IdentifierChoices.choices)
    password = models.TextField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100,
        choices=UserAccountStatusChoices,
        default=UserAccountStatusChoices.INACTIVE
    )

    class Meta:
        db_table = 'user_account'
        ordering = ['cursor']

    def __str__(self):
        return 'Account ' + self.identifier


class RevokedToken(BaseModel):
    token = models.TextField(db_index=True, unique=True)
    expires_on = models.DateTimeField()
