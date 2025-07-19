from sqlmodel import select, and_
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.appointment import Appointment, AppointmentCreate, AppointmentStatus
from app.models.user import User, UserType
from app.dependencies import SessionDep


def create_appointment(
    session: SessionDep,
    appointment: AppointmentCreate,
    current_user_id: int,
) -> Appointment:
    # Verify patient_id matches current user (unless admin)
    if current_user_id != appointment.patient_id:
        current_user = session.get(User, current_user_id)
        if not current_user or current_user.user_type != UserType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only book appointments for yourself",
            )

    if appointment.patient_id == appointment.doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot book an appointment with yourself",
        )

    doctor = session.get(User, appointment.doctor_id)
    if not doctor or doctor.user_type != UserType.doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )

    if not is_doctor_available(
        session, appointment.doctor_id, appointment.appointment_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not available at this timeslot",
        )

    if has_overlapping_appointment(
        session, appointment.doctor_id, appointment.appointment_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This timeslot is already booked",
        )

    db_appointment = Appointment(**appointment.model_dump())
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)
    return db_appointment


def is_doctor_available(
    session: SessionDep, doctor_id: int, appointment_time: datetime
) -> bool:
    doctor = session.get(User, doctor_id)
    if not doctor or not doctor.available_timeslots:
        return False

    start_str, end_str = doctor.available_timeslots.split("-")
    start_hour = int(start_str.split(":")[0])
    end_hour = int(end_str.split(":")[0])

    return start_hour <= appointment_time.hour < end_hour


def has_overlapping_appointment(
    session: SessionDep, doctor_id: int, appointment_time: datetime
) -> bool:
    start_window = appointment_time - timedelta(minutes=30)
    end_window = appointment_time + timedelta(minutes=30)

    statement = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_window,
            Appointment.appointment_date <= end_window,
            Appointment.status != AppointmentStatus.cancelled,
        )
    )
    return session.exec(statement).first() is not None


def get_appointments_for_user(session: SessionDep, user_id: int, user_type: UserType):
    if user_type == UserType.doctor:
        statement = select(Appointment).where(Appointment.doctor_id == user_id)
    else:
        statement = select(Appointment).where(Appointment.patient_id == user_id)

    appointments = session.exec(statement).all()
    return appointments


def update_appointment_status(
    session: SessionDep,
    appointment_id: int,
    new_status: AppointmentStatus,
    current_user_id: int,
    current_user_type: UserType,
):
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Patients can only cancel their own appointments
    if current_user_type == UserType.patient:
        if appointment.patient_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this appointment",
            )
        if new_status != AppointmentStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only cancel appointments",
            )

    # Doctors can only update their own appointments
    if (
        current_user_type == UserType.doctor
        and appointment.doctor_id != current_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment",
        )

    appointment.status = new_status
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment
