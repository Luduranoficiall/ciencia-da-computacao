"""Auditoria administrativa: acoes fechadas (Enum) e gravacao append-only."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditAction(str, Enum):
    """Conjunto fechado — unica fonte de verdade para nomes gravados na BD e filtros API."""

    SESSIONS_REVOKED = "sessions_revoked"
    STUDENT_CREATED = "student_created"
    STUDENT_UPDATED = "student_updated"
    MODULE_UPSERTED = "module_upserted"
    CURRICULUM_SYNCED = "curriculum_synced"
    CERTIFICATE_PDF_DOWNLOADED = "certificate_pdf_downloaded"


# Compatibilidade com importacoes existentes `from app.audit_service import SESSIONS_REVOKED`
SESSIONS_REVOKED = AuditAction.SESSIONS_REVOKED.value
STUDENT_CREATED = AuditAction.STUDENT_CREATED.value
STUDENT_UPDATED = AuditAction.STUDENT_UPDATED.value
MODULE_UPSERTED = AuditAction.MODULE_UPSERTED.value
CURRICULUM_SYNCED = AuditAction.CURRICULUM_SYNCED.value
CERTIFICATE_PDF_DOWNLOADED = AuditAction.CERTIFICATE_PDF_DOWNLOADED.value

AUDIT_ACTION_VALUES: frozenset[str] = frozenset(a.value for a in AuditAction)


def _client_ip(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def record_audit_log(
    db: Session,
    *,
    actor_user_id: int,
    action: AuditAction,
    target_user_id: int | None = None,
    detail: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    """Grava uma linha de auditoria. `action` tem de ser membro de `AuditAction`."""
    rid = getattr(request.state, "request_id", None) if request else None
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action.value,
            target_user_id=target_user_id,
            detail_json=json.dumps(detail) if detail is not None else None,
            request_id=rid,
            ip_address=_client_ip(request),
        )
    )
