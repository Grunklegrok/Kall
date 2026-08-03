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
    totp_secret_encrypted: str | None = None
    totp_enabled: bool = False


class UserSession(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime
    revoked_at: datetime | None = None


class OAuthIdentity(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    provider: str = Field(index=True)
    provider_subject: str = Field(index=True)
    email: str | None = Field(default=None, index=True)


class PasskeyCredential(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    name: str = "Passkey"
    credential_id: str = Field(index=True, unique=True)
    public_key: str
    sign_count: int = 0
    transports: str | None = None
    last_used_at: datetime | None = None


class AuthChallenge(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, index=True, foreign_key="user.id")
    purpose: str = Field(index=True)
    challenge: str = Field(index=True, unique=True)
    expires_at: datetime
    consumed_at: datetime | None = None
