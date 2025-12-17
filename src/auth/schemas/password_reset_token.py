from datetime import datetime

from pydantic import BaseModel

from auth.schemas.user_account import RequiredStr


class ChangePassword(BaseModel):
    password: RequiredStr


class ResetPassword(ChangePassword):
    token: str


class PasswordResetTokenRepoCreate(BaseModel):
    reset_password_token: str
    expires_on: datetime
    user_account_id: int
