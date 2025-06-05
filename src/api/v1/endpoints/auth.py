from datetime import timedelta
from typing import Annotated, Type

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.debs import SessionDep
from core import security
from core.config import configs
from crud import user as crud
from crud.user import get_user_by_email

router = APIRouter(prefix="/auth", tags=["user"])


@router.post("/login/access-token")
def login_access_token(
        session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    db_user = get_user_by_email(session=session, email=form_data.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = security.create_access_token(user.id, expires_delta=access_token_expires)

    return {"token": token, "username": user.full_name, "user_id": user.id}



@router.post("/login")
def login_access_token(
        session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # access_token_expires = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"message": "Login successful.", "username": user.full_name, "user_id": user.id}
