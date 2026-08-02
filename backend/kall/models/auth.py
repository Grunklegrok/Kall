from datetime import datetime

from sqlmodel import Field

from kall.models.core import TimestampMixin


class UserCredential(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id", unique=True)
    password_hash: str
    email_verified: bool = False
    verification_token_hash: str | None = Field(default=None, index=True)
    reset_token_hash: str | None = Field(default=None, index=True)
    reset_token_expires_at: datetime | None = None
    failed_login_count: int = 0
    locked_until: datetime | None = None


class UserSession(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime
    revoked_at: datetime | None = None
