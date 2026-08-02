from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str = "change-me"
    database_url: str = "sqlite:///./kall.db"
    frontend_url: str = "http://localhost:3000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.1-mini"
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id: str | None = None
    sensitive_data_encryption_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
