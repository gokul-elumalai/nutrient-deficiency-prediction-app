import uuid

from sqlmodel import Session

from crud.user_details import update_user_nutrition_summary
from models.food_log import FoodLogCreate, FoodLog


def create_food_log(*, session: Session, food_log: FoodLogCreate, user_id: uuid.UUID) -> FoodLog:
    db_obj = FoodLog.model_validate(food_log, update={"user_id": user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Update summary after insertion
    update_user_nutrition_summary(session, user_id)

    return db_obj


