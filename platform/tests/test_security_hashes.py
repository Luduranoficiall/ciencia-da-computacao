import bcrypt

from app.security import hash_password, maybe_rehash_password_after_verify, verify_password


def test_argon2_hash_and_verify_roundtrip():
    p = "Str0ng!Pass-x"
    h = hash_password(p)
    assert h.startswith("$argon2")
    assert verify_password(p, h)
    assert not verify_password("wrong", h)


def test_bcrypt_legacy_verify_and_rehash_signal():
    p = "studentpass12"
    legacy = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode()
    assert verify_password(p, legacy)
    assert not verify_password("nope", legacy)
    new_h = maybe_rehash_password_after_verify(p, legacy)
    assert new_h is not None
    assert new_h.startswith("$argon2")


def test_argon2_rehash_returns_none_when_current():
    p = "SamePass!9"
    h = hash_password(p)
    assert verify_password(p, h)
    assert maybe_rehash_password_after_verify(p, h) is None
