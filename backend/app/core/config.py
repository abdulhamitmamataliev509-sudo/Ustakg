"""Application settings loaded from environment variables via Pydantic Settings."""
from functools import lru_cache
from typing import Annotated, List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    Values are read from environment variables and/or a local ``.env`` file
    (see ``backend/.env.example``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Usta kg"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = ""  # REQUIRED — set via env/.env (see .env.example)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ustakg_db"
    POSTGRES_PORT: int = 5432
    # Optional full URL; when set it overrides the individual parts above.
    POSTGRES_URL: str = ""

    # CORS
    # NoDecode keeps comma-separated strings flowing into the validator below
    # instead of attempting JSON decoding first.
    CORS_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:8081",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def _secret_key_required(cls, v: str) -> str:
        """Refuse to boot with an unset SECRET_KEY (empty string default)."""
        if not v:
            raise ValueError(
                "SECRET_KEY must be provided — copy .env.example to .env and set it"
            )
        return v

    @model_validator(mode="after")
    def _guard_insecure_production(self):
        """Never let the development placeholder reach a production run."""
        if (
            self.ENVIRONMENT == "production"
            and self.SECRET_KEY == "super-secret-key-change-in-production"
        ):
            raise ValueError(
                "SECRET_KEY must not use the development placeholder in production"
            )
        return self

    @property
    def database_url(self) -> str:
        """Resolved SQLAlchemy database URL."""
        if self.POSTGRES_URL:
            return self.POSTGRES_URL
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


settings = get_settings()
