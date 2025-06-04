from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models.food_log import FoodLog
from models.user_details import UserDetails
from src.api.v1.debs import CurrentUser, SessionDep
from prediction_engine import diet_predictor
router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/diet")
def predict_diet(
        *,
        session: SessionDep,
        current_user: CurrentUser
):
    """
    Predict diet plan based on user details
    """
    # Get user details from DB
    user_details = session.exec(
        select(UserDetails).where(UserDetails.user_id == current_user.id)
    ).first()

    query = select(FoodLog).where(FoodLog.user_id == current_user.id)
    food_logs = session.exec(query).all()

    if not user_details or not food_logs:
        raise HTTPException(
            status_code=404,
            detail="Please complete your health profile first"
        )

    return {"recommendation": diet_predictor.predict(user_details, food_log_count=len(food_logs))}