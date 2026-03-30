"""Invariantes do modulo de auditoria (acoes fechadas)."""

import pytest

from app.audit_service import AUDIT_ACTION_VALUES, AuditAction


def test_audit_action_enum_exhaustive_values() -> None:
    assert len(AuditAction) == len(AUDIT_ACTION_VALUES)
    for a in AuditAction:
        assert a.value in AUDIT_ACTION_VALUES


def test_audit_action_construct_from_value() -> None:
    assert AuditAction("sessions_revoked") is AuditAction.SESSIONS_REVOKED
    assert AuditAction("student_created") is AuditAction.STUDENT_CREATED


def test_audit_action_invalid_value_raises() -> None:
    with pytest.raises(ValueError):
        AuditAction("not_a_real_action")
