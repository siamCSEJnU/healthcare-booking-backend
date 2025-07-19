import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserRead, UserType, UserCreate, UserUpdate
from app.utils.auth import get_password_hash
from app.crud.user import update_user
from app.dependencies import (
    SessionDep,
    userCreateDP,
    get_current_user,
    get_current_admin,
    get_current_doctor,
    userUpdateDP,
    passwordChangeDP,
)
from app.models.token import Token

from app.utils.auth import create_access_token, verify_password
from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_mobile,
)


ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register_user(user: userCreateDP, session: SessionDep):
    if get_user_by_email(session, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_mobile(session, user.mobile):
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    profile_image_path = None
    if user.profile_image and user.profile_image.filename:
        if user.profile_image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")
        contents = user.profile_image.file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 5mb limit")

        extension = user.profile_image.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join("media/profile_images", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)
        profile_image_path = filepath

    user_data = user.model_dump(exclude={"profile_image"})
    user_data["profile_image"] = profile_image_path

    if user.user_type == UserType.doctor:
        required_fields = {
            "license_number": user.license_number,
            "experience_years": user.experience_years,
            "consultation_fee": user.consultation_fee,
            "available_timeslots": user.available_timeslots,
        }
        for field, value in required_fields.items():
            if value is None:
                raise HTTPException(
                    status_code=400, detail=f"{field} is required for doctors"
                )
    return create_user(session, UserCreate(**user_data))


@router.post("/login", response_model=Token)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    user = get_user_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.email, "role": user.user_type})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: Annotated[UserRead, Depends(get_current_user)]):
    return current_user


@router.get("/admin-dashboard", response_model=UserRead)
def admin_dashboard(admin_user: Annotated[UserRead, Depends(get_current_admin)]):
    return admin_user


@router.get("/doctor-dashboard", response_model=UserRead)
def admin_dashboard(doctor_user: Annotated[UserRead, Depends(get_current_doctor)]):
    return doctor_user


@router.patch("/me", response_model=UserRead)
def update_my_profile(
    session: SessionDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    update_data: userUpdateDP,
):
    # Handle profile image upload if provided
    profile_image_path = current_user.profile_image
    if update_data.profile_image:
        if update_data.profile_image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

        contents = update_data.profile_image.file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 5mb limit")

        # Delete old image if it exists
        if profile_image_path and os.path.exists(profile_image_path):
            os.remove(profile_image_path)

        # Save new image
        extension = update_data.profile_image.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join("media/profile_images", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)

        profile_image_path = filepath

    # Prepare update data
    user_update = update_data.model_dump(exclude={"profile_image"}, exclude_unset=True)
    if profile_image_path:
        user_update["profile_image"] = profile_image_path

    return update_user(
        session, current_user.id, UserUpdate(**user_update), current_user
    )


@router.patch("/{user_id}", response_model=UserRead)
def update_user_profile(
    user_id: int,
    session: SessionDep,
    update_data: userUpdateDP,
    current_user: Annotated[UserRead, Depends(get_current_admin)],
):
    # Similar to above but only accessible by admin
    profile_image_path = None
    if update_data.profile_image:
        if update_data.profile_image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

        contents = update_data.profile_image.file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 5mb limit")

        # Delete old image if it exists
        if profile_image_path and os.path.exists(profile_image_path):
            os.remove(profile_image_path)

        # Save new image
        extension = update_data.profile_image.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join("media/profile_images", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)

        profile_image_path = filepath
    user_update = update_data.model_dump(exclude={"profile_image"}, exclude_unset=True)
    if profile_image_path:
        user_update["profile_image"] = profile_image_path

    return update_user(session, user_id, UserUpdate(**user_update), current_user)


@router.post("/me/change-password")
def change_password(
    password_update: passwordChangeDP,
    session: SessionDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    if not verify_password(
        password_update.current_password, current_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    hashed_password = get_password_hash(password_update.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return {"message": "Password updated successfully"}
