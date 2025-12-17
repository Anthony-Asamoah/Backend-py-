from django.db import models

from main.utils.base_classes import BaseModel


class PasswordResetToken(BaseModel):
    reset_password_token = models.TextField(db_index=True, unique=True)
    expires_on = models.DateTimeField()
    user_account = models.ForeignKey(
        "auth.UserAccount",
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )

    def __str__(self):
        return f'Reset pwd token for user {self.user_account.identifier}'
