from django.db import models

from auth.schema import UserAccountStatusChoices
from main.utils.base_classes import BaseModel


class UserAccount(BaseModel):
    identifier = models.CharField(max_length=100)
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

    @property
    def identifier_type(self):
        from auth.utils import detect_identifier_type
        return detect_identifier_type(self.identifier)


class RevokedToken(BaseModel):
    token = models.TextField(db_index=True, unique=True)
    expires_on = models.DateTimeField()


class PasswordResetToken(BaseModel):
    reset_password_token = models.TextField(db_index=True, unique=True)
    expires_on = models.DateTimeField()
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='password_reset_tokens')

    def __str__(self):
        return f'Reset pwd token for user {self.user_account.identifier}'
