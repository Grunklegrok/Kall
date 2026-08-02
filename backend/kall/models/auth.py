from datetime import datetime
from sqlmodel import Field
from kall.models.core import TimestampMixin

class UserCredential(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id", unique=True)
    password_hash: str
    email_verified: bool = False

class UserSession(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime
    revoked_at: datetime | None = None
