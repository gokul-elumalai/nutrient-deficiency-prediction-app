import uuid

from sqlmodel import Session, select

from models.food_log import FoodLog
from models.user_details import UserDetailsCreate, UserDetails


def create_user_details(*, session: Session, user_details: UserDetailsCreate, user_id: uuid.UUID) -> FoodLog:
    db_obj = UserDetails.model_validate(user_details, update={"user_id": user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user_nutrition_summary(session: Session, user_id: uuid.UUID):
    # Sum up the nutrition from all food logs of the user
    statement = select(
        FoodLog.calories,
        FoodLog.protein,
        FoodLog.fat,
        FoodLog.carbs
    ).where(FoodLog.user_id == user_id)

    results = session.exec(statement).all()

    total_calories = sum(row.calories for row in results)
    total_protein = sum(row.protein for row in results)
    total_fat = sum(row.fat for row in results)
    total_carbs = sum(row.carbs for row in results)

    # Fetch user details to update
    user_details = session.exec(select(UserDetails).where(UserDetails.user_id == user_id)).first()

    if user_details:
        user_details.calorie_intake = total_calories
        user_details.protein_intake = total_protein
        user_details.fat_intake = total_fat
        user_details.carbohydrate_intake = total_carbs

        session.add(user_details)
        session.commit()
        session.refresh(user_details)
