import datetime
from typing import Annotated, Optional

from django.db.models.enums import TextChoices
from pydantic import AfterValidator, BaseModel, EmailStr, UUID4

from main.utils.base_classes import BaseOutSchema
from main.utils.validators import validate_phone_number, validate_str

# Custom type for validated phone numbers
PhoneNumber = Annotated[str, AfterValidator(validate_phone_number)]


class GenderChoices(TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class UserInfoBase(BaseModel):
    title: str
    last_name: str
    first_name: str
    other_names: Optional[str] = None
    date_of_birth: datetime.date
    gender: GenderChoices
    nationality: str
    email: EmailStr
    phone_number: PhoneNumber

    class Config:
        from_attributes = True
        exclude_unset = True


class UserInfoRepoCreate(UserInfoBase):
    id: Optional[UUID4] = None


class UserInfoCreate(UserInfoBase):
    title: Annotated[str, AfterValidator(validate_str)]
    last_name: Annotated[str, AfterValidator(validate_str)]
    first_name: Annotated[str, AfterValidator(validate_str)]
    other_names: Annotated[Optional[str], AfterValidator(validate_str)] = None
    date_of_birth: datetime.date
    gender: GenderChoices
    nationality: Annotated[str, AfterValidator(validate_str)]
    email: Annotated[EmailStr, AfterValidator(validate_str)]
    phone_number: PhoneNumber


class UserInfoUpdate(UserInfoBase):
    title: Annotated[Optional[str], AfterValidator(validate_str)] = None
    last_name: Annotated[Optional[str], AfterValidator(validate_str)] = None
    first_name: Annotated[Optional[str], AfterValidator(validate_str)] = None
    date_of_birth: Optional[datetime.date] = None
    gender: Optional[GenderChoices] = None
    nationality: Annotated[Optional[str], AfterValidator(validate_str)] = None
    email: Annotated[Optional[EmailStr], AfterValidator(validate_str)] = None
    phone_number: Optional[PhoneNumber] = None


class UserInfoOut(BaseOutSchema, UserInfoBase):
    age: str
