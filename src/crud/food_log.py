import uuid
from typing import Any

from pydantic import EmailStr
from sqlmodel import Session, func, select

from models.food_log import FoodLogCreate, FoodLog, FoodLogPublic
from src.core.security import get_password_hash, verify_password
from src.models.message import Message
from src.models.user import User, UserCreate, UsersPublic, UserUpdate


def create_food_log(*, session: Session, food_log: FoodLogCreate, user_id: uuid.UUID) -> FoodLog:
    db_obj = FoodLog.model_validate(food_log, update={"user_id": user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


