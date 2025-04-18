import uuid
from typing import Any

from pydantic import EmailStr
from sqlmodel import Session, func, select

from src.core.security import get_password_hash, verify_password
from src.models.message import Message
from src.models.user import User, UserCreate, UsersPublic, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(*, session: Session, email: EmailStr) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(
    *, session: Session, email: str | EmailStr, password: str
) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def update_user(*, session: Session, db_user: User, user_info: UserUpdate) -> Any:
    user_data = user_info.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(*, session: Session, db_user: User) -> Message:
    session.delete(db_user)
    session.commit()
    return Message(message="User deleted successfully")


def get_all_users(*, session: Session, skip: int, limit: int) -> UsersPublic:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)
