from __future__ import annotations
from enum import Enum
from datetime import datetime
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class AppointmentBase(SQLModel):
    doctor_id: int = Field(foreign_key="user.id")
    patient_id: int = Field(foreign_key="user.id")
    appointment_date: datetime
    notes: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.pending


class Appointment(AppointmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class AppointmentBookRequest(SQLModel):
    """Model for patient booking requests"""

    doctor_id: int
    appointment_date: datetime
    notes: Optional[str] = None

    @field_validator("appointment_date")
    def validate_appointment_date(cls, v):
        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        if v < datetime.now():
            raise ValueError("Appointment date cannot be in the past")
        return v


class AppointmentCreate(AppointmentBase):
    """For admin/doctor creating appointments"""

    pass


class AppointmentRead(AppointmentBase):
    id: int
    created_at: datetime
