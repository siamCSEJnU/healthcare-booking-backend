from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database import engine
from app.utils.auth import decode_access_token


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


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
