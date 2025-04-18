import os
import secrets
from typing import Annotated, Any

from pydantic import AnyUrl, BeforeValidator, EmailStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Configs(BaseSettings):
    # Define environment variables or default values for configuration
    ENV: str = "local"
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    PROJECT_NAME: str
    DESCRIPTION: str
    CORS_ALLOWED_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)]

    POSTGRES_ENGINE: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    FIRST_SUPERUSER: EmailStr | None = None
    FIRST_SUPERUSER_PASSWORD: str | None = None

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None


class TestConfigs(Configs):
    model_config = SettingsConfigDict(
        env_file="../../../.env.testing",
        env_ignore_empty=True,
        extra="ignore",
    )
    ENV: str = "test"


def get_configs(env: str = "local") -> Configs:
    """
    Return the settings object based on the environment.

    Parameters:
        env (str): The environment to retrieve the settings for. Defaults to "dev".

    Returns:
        Settings: The settings object based on the environment.

    Raises:
        ValueError: If the environment is invalid.
    """
    # logger.debug("getting settings for env: %s", env)

    if env.lower() in ["test", "t", "testing"]:
        return TestConfigs()  # type: ignore
    if env.lower() in ["local", "l"]:
        return Configs()  # type: ignore

    raise ValueError("Invalid environment. Must be 'test' or 'local.'")


_env = os.environ.get("ENV", "local")

configs = get_configs(env=_env)
