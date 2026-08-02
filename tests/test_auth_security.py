from kall.auth import password_hash, verify_password


def test_password_hash_uses_versioned_format() -> None:
    stored = password_hash("a-strong-password")
    assert stored.startswith("pbkdf2_sha256$310000$")
    assert verify_password("a-strong-password", stored)
    assert not verify_password("wrong-password", stored)


def test_malformed_password_hash_is_rejected() -> None:
    assert not verify_password("password", "malformed")
