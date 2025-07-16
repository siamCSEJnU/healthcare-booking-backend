from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, UserRead
from app.dependencies import SessionDep
from app.models.token import Token
from app.utils.auth import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_mobile


router = APIRouter()


@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, session: SessionDep):
    if get_user_by_email(session, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_mobile(session, user.mobile):
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    return create_user(session, user)


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
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
