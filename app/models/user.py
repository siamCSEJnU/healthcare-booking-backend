from sqlmodel import SQLModel, Field
from enum import Enum
from fastapi import File, UploadFile, Form
from typing import Annotated
from pydantic import field_validator, EmailStr


class UserType(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class UserBase(SQLModel):
    full_name: str = Field(max_length=100)
    email: EmailStr = Field(index=True, unique=True)
    mobile: str = Field(max_length=14, min_length=11, index=True, unique=True)
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
