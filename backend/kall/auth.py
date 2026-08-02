import hashlib, hmac, secrets
from datetime import datetime, timedelta
from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select
from kall.db import get_session
from kall.models import User, UserCredential, UserSession

def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def password_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"

def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    actual = password_hash(password, salt).split("$", 1)[1]
    return hmac.compare_digest(actual, digest)

def create_session(session: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    session.add(UserSession(user_id=user_id, token_hash=hash_secret(token), expires_at=datetime.utcnow()+timedelta(days=30)))
    session.commit(); return token

def get_current_user(authorization: str | None = Header(default=None), session: Session = Depends(get_session)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    token = authorization.removeprefix("Bearer ").strip()
    row = session.exec(select(UserSession).where(UserSession.token_hash == hash_secret(token))).first()
    if not row or row.revoked_at or row.expires_at <= datetime.utcnow():
        raise HTTPException(401, "Invalid or expired session")
    user = session.get(User, row.user_id)
    if not user or not user.is_active: raise HTTPException(401, "Inactive user")
    return user
