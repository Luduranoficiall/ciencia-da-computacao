from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain[:72].encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain[:72].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def validate_password_strength(plain: str) -> None:
    if settings.password_require_upper and not re.search(r"[A-Z]", plain):
        raise ValueError("A palavra-passe deve conter pelo menos uma letra maiuscula.")
    if settings.password_require_lower and not re.search(r"[a-z]", plain):
        raise ValueError("A palavra-passe deve conter pelo menos uma letra minuscula.")
    if settings.password_require_digit and not re.search(r"[0-9]", plain):
        raise ValueError("A palavra-passe deve conter pelo menos um numero.")
    if settings.password_require_symbol and not re.search(r"[^A-Za-z0-9]", plain):
        raise ValueError("A palavra-passe deve conter pelo menos um simbolo.")


def create_access_token(sub: str, role: str, user_id: int, token_version: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": sub,
        "role": role,
        "uid": user_id,
        "tv": int(token_version),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def get_fernet() -> Fernet:
    key = (settings.content_encryption_key or "").strip()
    if not key:
        raise RuntimeError("CONTENT_ENCRYPTION_KEY em falta (Fernet). Ver .env.example")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_content(plaintext: str) -> bytes:
    return get_fernet().encrypt(plaintext.encode("utf-8"))


def decrypt_content(ciphertext: bytes) -> str:
    try:
        return get_fernet().decrypt(ciphertext).decode("utf-8")
    except InvalidToken as e:
        raise ValueError("Falha ao desencriptar (chave errada ou dados corrompidos)") from e
