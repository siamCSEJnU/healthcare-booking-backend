from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, status, HTTPException, File, UploadFile, Form
from app.models.user import UserType
from fastapi.security import OAuth2PasswordBearer
from app.database import engine
from app.utils.auth import decode_access_token
from app.models.user import UserCreateForm


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def user_create_dep(
    full_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    mobile: Annotated[str, Form()],
    user_type: Annotated[UserType, Form()],
    division: Annotated[str | None, Form()] = None,
    district: Annotated[str | None, Form()] = None,
    thana: Annotated[str | None, Form()] = None,
    profile_image: Annotated[UploadFile | None, File()] = None,
    license_number: Annotated[str | None, Form()] = None,
    experience_years: Annotated[int | None, Form()] = None,
    consultation_fee: Annotated[float | None, Form()] = None,
    available_timeslots: Annotated[str | None, Form()] = None,
) -> UserCreateForm:
    return UserCreateForm(
        full_name=full_name,
        email=email,
        password=password,
        mobile=mobile,
        user_type=user_type,
        division=division,
        district=district,
        thana=thana,
        profile_image=profile_image,
        license_number=license_number,
        experience_years=experience_years,
        consultation_fee=consultation_fee,
        available_timeslots=available_timeslots,
    )


userCreateDP = Annotated[UserCreateForm, Depends(user_create_dep)]


def get_current_user(token: Annotated[str, Depends(oauth_scheme)], session: SessionDep):
    from app.crud.user import get_user_by_email

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)

    if not payload:
        raise credentials_exception

    email = payload.get("sub")
    if not email:
        raise credentials_exception

    user = get_user_by_email(session, email)
    if not user:
        raise credentials_exception

    return user
