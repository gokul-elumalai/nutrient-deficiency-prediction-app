from sqlmodel import Session, create_engine, select

from crud import user as crud
from src.core.config import configs
from src.models.user import User, UserCreate

engine = create_engine(str(configs.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:

    user = session.exec(
        select(User).where(User.email == configs.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=configs.FIRST_SUPERUSER,
            password=configs.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
