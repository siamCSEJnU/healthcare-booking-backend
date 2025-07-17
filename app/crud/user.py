from sqlmodel import select
from app.models.user import User, UserCreate, UserRead
from app.utils.auth import get_password_hash
from app.dependencies import SessionDep


def get_user_by_email(session: SessionDep, email: str):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_mobile(session: SessionDep, mobile: str):
    statement = select(User).where(User.mobile == mobile)
    return session.exec(statement).first()


def create_user(session: SessionDep, user: UserCreate) -> UserRead:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        **user.model_dump(exclude={"password"}), hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
