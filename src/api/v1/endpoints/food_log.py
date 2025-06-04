import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, func

from models.message import Message
from src.api.v1.debs import CurrentUser, SessionDep, get_current_active_superuser
from models.food_log import FoodLog, FoodLogCreate, FoodLogPublic, FoodLogUpdate, FoodLogsPublic
from src.crud import food_log as crud

router = APIRouter(prefix="/food-log", tags=["food_log"])


@router.post(
    "/",
    response_model=FoodLogPublic,
    status_code=status.HTTP_201_CREATED
)
def create_food_log(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        food_log_in: FoodLogCreate
) -> Any:
    """
    Create new food log entry for the current user.
    """

    food_log = crud.create_food_log(session=session, food_log=food_log_in, user_id=current_user.id)
    return food_log


@router.get("/{food_log_id}", response_model=FoodLogPublic)
def read_food_log_by_id(
        food_log_id: uuid.UUID,
        session: SessionDep,
        current_user: CurrentUser
) -> Any:
    """
    Get a specific food log by id.
    """
    food_log = session.get(FoodLog, food_log_id)
    if not food_log:
        raise HTTPException(
            status_code=404,
            detail="The food log with this id does not exist"
        )

    if food_log.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this food log"
        )

    return food_log


@router.patch("/{food_log_id}", response_model=FoodLogPublic)
def update_food_log(
        *,
        session: SessionDep,
        food_log_id: uuid.UUID,
        food_log_in: FoodLogUpdate,
        current_user: CurrentUser
) -> Any:
    """
    Update a food log entry.
    """
    db_food_log = session.get(FoodLog, food_log_id)
    if not db_food_log:
        raise HTTPException(
            status_code=404,
            detail="The food log with this id does not exist"
        )

    if db_food_log.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this food log"
        )

    # Update only provided fields
    update_data = food_log_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_food_log, field, value)

    session.add(db_food_log)
    session.commit()
    session.refresh(db_food_log)
    return db_food_log


@router.delete("/{food_log_id}", response_model=Message)
def delete_food_log(
        *,
        session: SessionDep,
        food_log_id: uuid.UUID,
        current_user: CurrentUser
) -> Message:
    """
    Delete a food log entry.
    """
    food_log = session.get(FoodLog, food_log_id)
    if not food_log:
        raise HTTPException(status_code=404, detail="Food log not found")

    if food_log.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this food log"
        )

    session.delete(food_log)
    session.commit()
    return Message(detail="Food log deleted successfully")


@router.get("/", response_model=FoodLogsPublic)
def read_food_logs(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 100,
        date_from: date = None,
        date_to: date = None,
        meal_type: str = None
) -> Any:
    """
    Retrieve food logs for the current user.
    """
    query = select(FoodLog).where(FoodLog.user_id == current_user.id)

    # Apply filters
    if date_from:
        query = query.where(FoodLog.log_date >= date_from)
    if date_to:
        query = query.where(FoodLog.log_date <= date_to)
    if meal_type:
        query = query.where(FoodLog.meal_type == meal_type.lower())

    food_logs = session.exec(query.offset(skip).limit(limit)).all()

    # For superusers to see all logs
    if current_user.is_superuser and (date_from or date_to or meal_type):
        admin_query = select(FoodLog)
        if date_from:
            admin_query = admin_query.where(FoodLog.log_date >= date_from)
        if date_to:
            admin_query = admin_query.where(FoodLog.log_date <= date_to)
        if meal_type:
            admin_query = admin_query.where(FoodLog.meal_type == meal_type.lower())

        food_logs = session.exec(admin_query.offset(skip).limit(limit)).all()

    return FoodLogsPublic(data=food_logs, count=len(food_logs))


@router.get("/latest/")
def read_latest_food_logs(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    # Get the most recent log_date for the user
    latest_date_query = select(func.max(FoodLog.log_date)).where(FoodLog.user_id == current_user.id)
    latest_log_date = session.exec(latest_date_query).one()

    if not latest_log_date:
        return []

    from_date = latest_log_date - timedelta(days=6)  # Includes today + 6 previous days
    to_date = latest_log_date

    # Query for the logs in that range
    query = select(FoodLog).where(
        FoodLog.user_id == current_user.id,
        FoodLog.log_date >= from_date,
        FoodLog.log_date <= to_date
    )

    food_logs = session.exec(query.offset(skip).limit(limit)).all()
    return food_logs



RECOMMENDED_VALUES = {
    "calories": 2000,
    "protein": 50,
    "fat": 70,
    "carbs": 300,
    "fiber": 30,
    "sugar": 50,
    "sodium": 2300,
    "potassium": 4700,
    "iron": 18,
    "calcium": 1000,
    "vitamin_a": 3000,
    "vitamin_c": 90
}


@router.get("/nutrition-summary/")
def get_nutrition_summary(*, session: SessionDep, current_user=CurrentUser):
    latest_date_query = select(func.max(FoodLog.log_date)).where(FoodLog.user_id == current_user.id)
    latest_log_date = session.exec(latest_date_query).one()

    if not latest_log_date:
        return []

    from_date = latest_log_date - timedelta(days=6)  # Includes today + 6 previous days
    to_date = latest_log_date

    query = select(FoodLog).where(
        FoodLog.user_id == current_user.id,
                    FoodLog.log_date >= from_date,
                    FoodLog.log_date <= to_date
    )
    logs = session.exec(query).all()

    totals = defaultdict(float)
    days = set()

    for log in logs:
        days.add(log.log_date)
        for field in RECOMMENDED_VALUES:
            value = getattr(log, field, 0)
            if value:
                totals[field] += value

    num_days = len(days) or 1
    daily_avg = {nutrient: round(totals[nutrient] / num_days, 2) for nutrient in RECOMMENDED_VALUES}

    return {"average": daily_avg, "recommended": RECOMMENDED_VALUES}
