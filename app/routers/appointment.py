from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Annotated
from datetime import datetime
from app.models.appointment import (
    AppointmentBookRequest,
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatus,
)
from app.models.user import UserType, UserRead
from app.crud.appointment import (
    create_appointment,
    get_appointments_for_user,
    update_appointment_status,
    is_doctor_available,
    has_overlapping_appointment,
)
from app.dependencies import SessionDep, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/book", response_model=AppointmentRead)
def book_appointment(
    book_request: AppointmentBookRequest,
    session: SessionDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    if current_user.user_type != UserType.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments",
        )

    appointment_data = AppointmentCreate(
        **book_request.model_dump(),
        patient_id=current_user.id,
        status=AppointmentStatus.pending
    )

    return create_appointment(session, appointment_data, current_user.id)


@router.get("/my-appointments", response_model=List[AppointmentRead])
def get_my_appointments(
    session: SessionDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    return get_appointments_for_user(session, current_user.id, current_user.user_type)


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_status(
    appointment_id: int,
    new_status: AppointmentStatus,
    session: SessionDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    return update_appointment_status(
        session, appointment_id, new_status, current_user.id, current_user.user_type
    )


@router.get("/doctor/{doctor_id}/availability")
def check_doctor_availability(
    doctor_id: int,
    date: datetime,
    session: SessionDep,
):
    doctor = session.get(User, doctor_id)
    if not doctor or doctor.user_type != UserType.doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    is_available = is_doctor_available(session, doctor_id, date)
    is_booked = has_overlapping_appointment(session, doctor_id, date)

    return {
        "is_available": is_available,
        "is_booked": is_booked,
        "available_slots": doctor.available_timeslots,
    }
