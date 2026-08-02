import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from kall.config import get_settings
from kall.db import get_session
from kall.models import User, UserSession


def utcnow() -> datetime:
    return datetime.utcnow()


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def password_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 310_000).hex()
    return f"pbkdf2_sha256$310000${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations)).hex()
    return hmac.compare_digest(candidate, expected)


def create_session(session: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    settings = get_settings()
    session.add(UserSession(user_id=user_id, token_hash=hash_secret(token), expires_at=utcnow() + timedelta(days=settings.session_days)))
    session.commit()
    return token


def revoke_session(session: Session, token: str) -> None:
    row = session.exec(select(UserSession).where(UserSession.token_hash == hash_secret(token))).first()
    if row and row.revoked_at is None:
        row.revoked_at = utcnow()
        session.add(row)
        session.commit()


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    return authorization.removeprefix("Bearer ").strip()


def get_current_user(authorization: str | None = Header(default=None), session: Session = Depends(get_session)) -> User:
    token = bearer_token(authorization)
    row = session.exec(select(UserSession).where(UserSession.token_hash == hash_secret(token))).first()
    if not row or row.revoked_at or row.expires_at <= utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = session.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


def new_one_time_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_secret(token)
