from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App Settings
    app_name: str = "LangGpt"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # PostgreSQL Database Config
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "lang_gpt_admin"
    postgres_password: str = ""
    postgres_db: str = "lang_gpt_db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Used by Alembic (sync driver)"""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # JWT configuration
    jwt_secret_key: str = ""  # Required — set in .env via: openssl rand -hex 32
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # Google OAuth credentials
    google_client_id: str = ""
    google_client_secret: str = ""

    # AI (Gemini) API key
    gemini_api_key: str = ""

    # Security settings
    allowed_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 60

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()