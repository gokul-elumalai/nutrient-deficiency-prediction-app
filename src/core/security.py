import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from core.config import configs

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pwd_bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    hashed_pwd_string = base64.b64encode(hashed_pwd_bytes).decode("utf-8")
    return hashed_pwd_string


def verify_password(plain_password: str, hashed_pwd_string: str) -> bool:
    password_byte_enc = plain_password.encode("utf-8")
    hashed_pwd_bytes = base64.b64decode(hashed_pwd_string)
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_pwd_bytes)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, configs.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
