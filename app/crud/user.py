from sqlmodel import select
from app.models.user import User, UserCreate, UserRead, UserUpdate, UserType
from app.utils.auth import get_password_hash
from app.dependencies import SessionDep
from fastapi import HTTPException, status


def get_user_by_email(session: SessionDep, email: str) -> UserRead:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_mobile(session: SessionDep, mobile: str) -> UserRead:
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


def update_user(
    session: SessionDep, user_id: int, user_update: UserUpdate, current_user: User
) -> UserRead:

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions (admin can update anyone, users can only update themselves)
    if current_user.user_type != UserType.admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    # Check if new email or mobile already exists
    if user_update.email and user_update.email != db_user.email:
        if get_user_by_email(session, user_update.email):
            raise HTTPException(status_code=400, detail="Email already registered")

    if user_update.mobile and user_update.mobile != db_user.mobile:
        if get_user_by_mobile(session, user_update.mobile):
            raise HTTPException(
                status_code=400, detail="Mobile number already registered"
            )

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
