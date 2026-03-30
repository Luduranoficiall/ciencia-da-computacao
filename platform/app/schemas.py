from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    """Corpo opcional quando o cliente nao usa cookie (ex.: app nativa)."""

    refresh_token: str | None = None


class OkOut(BaseModel):
    ok: bool = True


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = Field(default=None, max_length=512)


class AdminCreateStudentIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = Field(default=None, max_length=512)


class ModuleCreateIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=64)
    title: str = Field(max_length=512)
    body_markdown: str = Field(min_length=1)


class ModuleListOut(BaseModel):
    slug: str
    title: str


class ModuleContentOut(BaseModel):
    slug: str
    title: str
    body_markdown: str


class ProgressOut(BaseModel):
    module_slug: str
    completed_at: datetime


class StudentOverviewOut(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime
    completed_modules: list[str]
    has_certificate: bool
    certificate_serial: str | None
    active_sessions: int = Field(
        default=0,
        description="Refresh tokens ainda validos (renovacao de sessao; aproxima dispositivos/sessoes).",
    )


class RevokeSessionsOut(BaseModel):
    user_id: int
    revoked_count: int


class AdminPatchStudentIn(BaseModel):
    full_name: str | None = Field(default=None, max_length=512)
    is_active: bool | None = None


class CertificateStatusOut(BaseModel):
    eligible: bool
    completed: int
    required: int
    has_certificate: bool
    serial_number: str | None
    issued_at: datetime | None


class PublicCertificateVerifyOut(BaseModel):
    serial_number: str
    valid: bool
    issued_at: datetime | None


class AuditLogOut(BaseModel):
    id: int
    actor_user_id: int
    action: str
    target_user_id: int | None
    detail: dict | None = None
    request_id: str | None = None
    ip_address: str | None = None
    created_at: datetime
