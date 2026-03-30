"""Refresh tokens opacos: armazenados como hash (SHA-256), rotacao na renovacao."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import RefreshToken, User
from app.security import create_access_token


def _as_utc(dt: datetime) -> datetime:
    """SQLite pode devolver datetimes naive; normaliza para UTC aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_refresh_credentials() -> tuple[str, str]:
    """Devolve (token_em_claro, family_id)."""
    return secrets.token_urlsafe(32), str(uuid.uuid4())


def create_refresh_token_row(db: Session, user_id: int) -> str:
    """Adiciona linha (sem commit). Devolve token em claro para o cookie."""
    raw, family_id = new_refresh_credentials()
    exp = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(
        RefreshToken(
            user_id=user_id,
            family_id=family_id,
            token_hash=hash_refresh_token(raw),
            expires_at=exp,
        )
    )
    return raw


def rotate_refresh_token(db: Session, raw_refresh: str) -> tuple[str, str]:
    """
    Revoga o refresh usado e cria novo. Devolve (novo_access_jwt, novo_refresh_claro).
    Levanta ValueError se invalido.
    """
    h = hash_refresh_token(raw_refresh)
    row = db.scalars(
        select(RefreshToken).where(
            RefreshToken.token_hash == h,
            RefreshToken.revoked_at.is_(None),
        )
    ).first()
    now = datetime.now(timezone.utc)
    if not row:
        raise ValueError("Refresh token invalido")
    if _as_utc(row.expires_at) <= now:
        raise ValueError("Refresh token expirado")

    user = db.get(User, row.user_id)
    if not user or not user.is_active:
        raise ValueError("Utilizador inativo")

    row.revoked_at = now
    new_raw = create_refresh_token_row(db, user.id)
    access = create_access_token(
        sub=user.email,
        role=user.role.value,
        user_id=user.id,
        token_version=user.access_token_version,
    )
    db.commit()
    return access, new_raw


def revoke_refresh_token(db: Session, raw_refresh: str) -> bool:
    h = hash_refresh_token(raw_refresh)
    row = db.scalars(
        select(RefreshToken).where(
            RefreshToken.token_hash == h,
            RefreshToken.revoked_at.is_(None),
        )
    ).first()
    if not row:
        return False
    row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return True


def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> int:
    """Revoga refresh tokens e invalida JWTs de access (incrementa access_token_version)."""
    now = datetime.now(timezone.utc)
    rows = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()
    for r in rows:
        r.revoked_at = now
    u = db.get(User, user_id)
    if u:
        u.access_token_version = int(u.access_token_version or 0) + 1
    db.commit()
    return len(rows)


def count_active_refresh_tokens(db: Session, user_id: int) -> int:
    """Refresh tokens nao revogados e ainda nao expirados (sessoes renovaveis)."""
    now = datetime.now(timezone.utc)
    rows = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()
    n = 0
    for r in rows:
        if _as_utc(r.expires_at) > now:
            n += 1
    return n
