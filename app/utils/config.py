from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Allow DATABASE_URL to be provided directly, or construct it from
    # individual DB_* environment variables (for backwards compatibility
    # with older .env files that expose db_host, db_port, etc.).
    DATABASE_URL: str | None = Field(None, env="DATABASE_URL")
    DB_HOST: str | None = Field(None, env="DB_HOST")
    DB_PORT: int | None = Field(None, env="DB_PORT")
    DB_NAME: str | None = Field(None, env="DB_NAME")
    DB_USER: str | None = Field(None, env="DB_USER")
    DB_PASSWORD: str | None = Field(None, env="DB_PASSWORD")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    # Optional API key for Gemini (LLM) integrations. Accepts value from
    # environment variable `GEMINI_API_KEY` or `.env` file. Optional to keep
    # backwards compatibility when not provided.
    GEMINI_API_KEY: str | None = Field(None, env="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()

    # If a DATABASE_URL wasn't provided but individual DB parts are,
    # construct a postgres URL. This helps environments that expose
    # credentials as separate variables (db_host, db_port, ...).
    if not s.DATABASE_URL and s.DB_HOST:
        user = s.DB_USER or ""
        password = s.DB_PASSWORD or ""
        host = s.DB_HOST
        port = s.DB_PORT or 5432
        name = s.DB_NAME or "postgres"
        # Build a DATABASE_URL that SQLAlchemy can consume. Empty user/pass
        # are omitted when not present.
        if user and password:
            s.DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        elif user:
            s.DATABASE_URL = f"postgresql://{user}@{host}:{port}/{name}"
        else:
            s.DATABASE_URL = f"postgresql://{host}:{port}/{name}"

    return s


settings = get_settings()

__all__ = ["Settings", "settings", "get_settings"]
