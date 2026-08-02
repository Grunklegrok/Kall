from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str = "change-me"
    database_url: str = "sqlite:///./kall.db"
    frontend_url: str = "http://localhost:3000"
    auto_create_tables: bool = True
    session_days: int = 30
    password_reset_minutes: int = 30
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.1-mini"
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id: str | None = None
    sensitive_data_encryption_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.app_env == "production":
            if self.app_secret_key == "change-me" or len(self.app_secret_key) < 32:
                raise ValueError("APP_SECRET_KEY must be at least 32 characters in production")
            if not self.sensitive_data_encryption_key:
                raise ValueError("SENSITIVE_DATA_ENCRYPTION_KEY is required in production")
            if self.database_url.startswith("sqlite"):
                raise ValueError("Production must use PostgreSQL or another server database")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
