import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from kall.config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    raw = settings.sensitive_data_encryption_key or settings.app_secret_key
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_sensitive(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_sensitive(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None
