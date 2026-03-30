"""Logica de negocio: conclusao, certificado idempotente."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.certificate_pdf import build_certificate_pdf, utc_now_iso
from app.config import settings
from app.curriculum_load import completion_fraction, load_required_module_slugs
from app.models import Certificate, CourseModule, StudentProgress, User
from app.security import decrypt_content


def required_slugs(db: Session) -> list[str]:
    del db  # API uniforme; pode evoluir para modulos na BD
    return load_required_module_slugs(settings.curriculum_json_path)


def slugs_with_modules(db: Session) -> set[str]:
    rows = db.scalars(select(CourseModule.slug)).all()
    return set(rows)


def user_completed_set(db: Session, user_id: int) -> set[str]:
    rows = db.scalars(select(StudentProgress.module_slug).where(StudentProgress.user_id == user_id)).all()
    return set(rows)


def is_fully_complete(db: Session, user_id: int) -> tuple[bool, int, int]:
    req = required_slugs(db)
    done = user_completed_set(db, user_id)
    have_modules = slugs_with_modules(db)
    missing_content = set(req) - have_modules
    if missing_content:
        return False, len(done & set(req)), len(req)
    c, t = completion_fraction(done, req)
    return c == t and t > 0, c, t


def holder_display_name(user: User) -> str:
    if user.full_name and user.full_name.strip():
        return user.full_name.strip()
    return user.email.split("@", 1)[0]


def issue_certificate_if_needed(db: Session, user: User) -> Certificate | None:
    """
    Idempotente: se ja existe certificado, devolve o existente.
    Se nao elegivel, devolve None.
    """
    existing = db.scalars(select(Certificate).where(Certificate.user_id == user.id)).first()
    if existing:
        return existing
    ok, _, _ = is_fully_complete(db, user.id)
    if not ok:
        return None
    serial = secrets.token_urlsafe(18).replace(".", "")[:32]
    issued = datetime.now(timezone.utc)
    pdf = build_certificate_pdf(
        holder_name=holder_display_name(user),
        serial=serial,
        issued_iso=utc_now_iso(),
    )
    cert = Certificate(
        user_id=user.id,
        serial_number=serial,
        issued_at=issued,
        holder_name=holder_display_name(user),
        pdf_blob=pdf,
    )
    db.add(cert)
    try:
        db.commit()
        db.refresh(cert)
        return cert
    except IntegrityError:
        db.rollback()
        return db.scalars(select(Certificate).where(Certificate.user_id == user.id)).first()


def get_module_plain(db: Session, slug: str) -> tuple[str, str]:
    row = db.scalars(select(CourseModule).where(CourseModule.slug == slug)).first()
    if not row:
        raise KeyError(slug)
    body = decrypt_content(row.ciphertext)
    return row.title, body
