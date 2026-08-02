import pytest
from pydantic import ValidationError

from kall.config import Settings


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", database_url="postgresql+psycopg://localhost/kall")


def test_production_requires_server_database() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            app_secret_key="x" * 32,
            sensitive_data_encryption_key="y" * 32,
            database_url="sqlite:///./kall.db",
        )
