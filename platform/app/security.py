from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

# Argon2id (OWASP): memoria elevada reduz utilidade de GPUs; custo de tempo moderado.
_argon2 = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

# JWT: tolerancia a pequenas diferencas de relogio entre servidores
_JWT_LEEWAY_S = 10


def verify_password(plain: str, hashed: str) -> bool:
    h = (hashed or "").strip()
    if not h:
        return False
    if h.startswith("$argon2"):
        try:
            _argon2.verify(h, plain)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
    # Legado bcrypt ($2a$, $2b$, $2y$)
    try:
        return bcrypt.checkpw(plain[:72].encode("utf-8"), h.encode("utf-8"))
    except ValueError:
        return False


def hash_password(plain: str) -> str:
    return _argon2.hash(plain)


def maybe_rehash_password_after_verify(plain: str, stored_hash: str) -> str | None:
    """Apos verify_password True: migrar bcrypt -> Argon2 ou atualizar parametros Argon2."""
    h = (stored_hash or "").strip()
    if h.startswith("$2"):
        return hash_password(plain)
    if h.startswith("$argon2"):
        try:
            if _argon2.check_needs_rehash(h):
                return hash_password(plain)
        except InvalidHashError:
            return hash_password(plain)
    return None


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
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        leeway=_JWT_LEEWAY_S,
        options={
            "require": ["exp", "iat", "sub"],
            "verify_signature": True,
        },
    )


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
