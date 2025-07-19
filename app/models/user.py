from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from fastapi import File, UploadFile, Form
from typing import Annotated
from pydantic import field_validator, EmailStr, BaseModel
from app.models.appointment import Appointment


class UserType(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class UserBase(SQLModel):
    full_name: str = Field(max_length=100)
    email: EmailStr = Field(index=True, unique=True)
    mobile: str = Field(max_length=14, min_length=14, index=True, unique=True)
    user_type: UserType
    division: str | None = None
    district: str | None = None
    thana: str | None = None
    profile_image: str | None = None
    is_active: bool = Field(default=True)
    license_number: str | None = None
    experience_years: int | None = None
    consultation_fee: int | None = None
    available_timeslots: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str

    @field_validator("mobile")
    def validate_mobile(cls, v):
        if not v.startswith("+88") or not v[1:].isdigit() or len(v) != 14:
            raise ValueError("Mobile must start with +88 and be exactly 14 digits")
        return v

    @field_validator("password")
    def validate_password(cls, val):
        if len(val) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in val):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in val):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+" for c in val):
            raise ValueError("Password must contain at least one special character")
        return val


class UserCreateForm(UserCreate):

    profile_image: UploadFile | None = None


class UserRead(UserBase):
    id: int


class UserUpdateBase(SQLModel):
    full_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, index=True, unique=True)
    mobile: str | None = Field(
        default=None, max_length=14, min_length=14, index=True, unique=True
    )
    division: str | None = None
    district: str | None = None
    thana: str | None = None
    is_active: bool | None = None
    license_number: str | None = None
    experience_years: int | None = None
    consultation_fee: float | None = None
    available_timeslots: str | None = None


class UserUpdate(UserUpdateBase):
    @field_validator("mobile")
    def validate_mobile(cls, v):
        if v is not None:
            if not v.startswith("+88") or not v[1:].isdigit() or len(v) != 14:
                raise ValueError("Mobile must start with +88 and be exactly 14 digits")
        return v


class UserUpdateForm(UserUpdate):
    profile_image: UploadFile | None = None


class PasswordChangeForm(SQLModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, val):
        if len(val) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in val):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in val):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+" for c in val):
            raise ValueError("Password must contain at least one special character")
        return val
