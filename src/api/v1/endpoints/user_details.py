from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List, Optional
import uuid
from datetime import date
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select

from models.message import Message
from src.api.v1.debs import CurrentUser, SessionDep
from src.crud import user_details as crud

from models.user_details import UserDetailsPublic, UserDetailsCreate, UserDetails, UserDetailsUpdate

router = APIRouter(prefix="/user-details", tags=["user_details"])


@router.post(
    "/",
    response_model=UserDetailsPublic,
    status_code=status.HTTP_201_CREATED
)
def create_user_details(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        details_in: UserDetailsCreate
) -> Any:
    """
    Create user details for the current user.
    """
    # Check if details already exist
    existing_details = session.exec(
        select(UserDetails).where(UserDetails.user_id == current_user.id)
    ).first()

    if existing_details:
        raise HTTPException(
            status_code=400,
            detail="User details already exist for this account"
        )

    user_details = crud.create_user_details(session=session, user_details=details_in, user_id=current_user.id)

    return user_details


@router.get("/", response_model=UserDetailsPublic)
def read_user_details(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        user_id: Optional[uuid.UUID] = None
) -> Any:
    """
    Get user details.
    Superusers can specify any user_id, regular users get their own details.
    """
    target_user_id = user_id if (user_id and current_user.is_superuser) else current_user.id

    details = session.exec(
        select(UserDetails).where(UserDetails.user_id == target_user_id)
    ).first()

    if not details:
        raise HTTPException(
            status_code=404,
            detail="User details not found"
        )

    return details


@router.patch("/", response_model=UserDetailsPublic)
def update_user_details(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        details_in: UserDetailsUpdate,
        user_id: Optional[uuid.UUID] = None
) -> Any:
    """
    Update user details.
    Superusers can specify any user_id, regular users can only update their own.
    """
    target_user_id = user_id if (user_id and current_user.is_superuser) else current_user.id

    details = session.exec(
        select(UserDetails).where(UserDetails.user_id == target_user_id)
    ).first()

    if not details:
        raise HTTPException(
            status_code=404,
            detail="User details not found"
        )

    # Update only provided fields
    update_data = details_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(details, field, value)

    # Recalculate BMI if height/weight changed
    if 'height_cm' in update_data or 'weight_kg' in update_data:
        if details.height_cm and details.weight_kg:
            details.bmi = round(details.weight_kg / ((details.height_cm / 100) ** 2), 1)

    session.add(details)
    session.commit()
    session.refresh(details)
    return details


@router.delete("/", response_model=Message)
def delete_user_details(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        user_id: Optional[uuid.UUID] = None
) -> Message:
    """
    Delete user details.
    Superusers can specify any user_id, regular users can only delete their own.
    """
    target_user_id = user_id if (user_id and current_user.is_superuser) else current_user.id

    details = session.exec(
        select(UserDetails).where(UserDetails.user_id == target_user_id)
    ).first()

    if not details:
        raise HTTPException(
            status_code=404,
            detail="User details not found"
        )

    session.delete(details)
    session.commit()
    return Message(detail="User details deleted successfully")


@router.get("/all", response_model=List[UserDetailsPublic])
def read_all_user_details(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 100
) -> Any:
    """
    Retrieve all user details (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can access all user details"
        )

    details = session.exec(
        select(UserDetails)
        .offset(skip)
        .limit(limit)
    ).all()

    return details
