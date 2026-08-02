from kall.auth import password_hash, verify_password

def test_password_hash_roundtrip():
    stored=password_hash("a-strong-password")
    assert verify_password("a-strong-password",stored)
    assert not verify_password("wrong-password",stored)
