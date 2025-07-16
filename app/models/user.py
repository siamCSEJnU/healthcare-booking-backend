from sqlmodel import SQLModel, Field
from enum import Enum


class UserType(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class UserBase(SQLModel):
    full_name: str = Field(max_length=100)
    email: str = Field(index=True, unique=True)
    mobile: str = Field(max_length=14, min_length=11, index=True, unique=True)
    user_type: UserType
    division: str | None = None
    district: str | None = None
    thana: str | None = None
    profile_image: str | None = None
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
