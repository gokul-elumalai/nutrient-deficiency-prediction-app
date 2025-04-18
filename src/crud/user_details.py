import uuid
from typing import Any

from pydantic import EmailStr
from sqlmodel import Session, func, select

from models.food_log import FoodLogCreate, FoodLog, FoodLogPublic
from models.user_details import UserDetailsCreate, UserDetails
from src.core.security import get_password_hash, verify_password
from src.models.message import Message
from src.models.user import User, UserCreate, UsersPublic, UserUpdate


def create_user_details(*, session: Session, user_details: UserDetailsCreate, user_id: uuid.UUID) -> FoodLog:
    db_obj = UserDetails.model_validate(user_details, update={"user_id": user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
