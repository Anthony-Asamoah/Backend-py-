from datetime import datetime
from typing import Annotated, Optional

from django.db.models.enums import TextChoices
from pydantic import AfterValidator, BaseModel, EmailStr

from main.utils.base_classes import BaseOutSchema
from main.utils.validators import validate_phone_number, validate_str
from user_info.schema import UserInfoOut

# Custom type for validated phone numbers
PhoneNumber = Annotated[str, AfterValidator(validate_phone_number)]
RequiredStr = Annotated[str, AfterValidator(validate_str)]


class IdentifierChoices(TextChoices):
    EMAIL = "EMAIL"
    PHONE_NUMBER = "PHONE_NUMBER"


class UserAccountStatusChoices(TextChoices):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class UserAccountBase(BaseModel):
    identifier: RequiredStr

    class Config:
        from_attributes = True
        exclude_unset = True


class UserAccountOut(BaseOutSchema, UserAccountBase):
    identifier_type: IdentifierChoices
    status: UserAccountStatusChoices
    is_deleted: bool
    created_on: datetime


class UserAccountCreate(UserAccountBase):
    password: RequiredStr


class Token(BaseModel):
    token: RequiredStr


class RefreshToken(Token):
    pass


class UserAccountTokens(BaseModel):
    access_token: str
    refresh_token: str


class UserAccountLogin(UserAccountBase):
    password: RequiredStr


class UserAccountLoginOut(UserAccountTokens):
    user_info: Optional[UserInfoOut] = None


class ResetPassword(BaseModel):
    password: RequiredStr


class ResetPasswordEmail(ResetPassword):
    email: EmailStr


class ResetPasswordPhoneNumber(ResetPassword):
    phone_number: PhoneNumber
