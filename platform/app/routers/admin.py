import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit_service import AuditAction, record_audit_log
from app.config import settings
from app.curriculum_load import load_required_module_slugs
from app.database import get_db
from app.deps import AdminUser
from app.models import AuditLog, Certificate, CourseModule, StudentProgress, User, UserRole
from app.schemas import (
    AdminCreateStudentIn,
    AdminPatchStudentIn,
    AuditLogOut,
    ModuleCreateIn,
    RevokeSessionsOut,
    StudentOverviewOut,
)
from app.security import encrypt_content, hash_password, validate_password_strength
from app.refresh_token_service import count_active_refresh_tokens, revoke_all_user_refresh_tokens
from app.services import user_completed_set

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-log", response_model=list[AuditLogOut])
def list_audit_log(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    action: AuditAction | None = Query(
        None,
        description="Filtrar por acao (conjunto fechado; ver AuditAction na API)",
    ),
) -> list[AuditLogOut]:
    del admin
    q = select(AuditLog)
    if action is not None:
        q = q.where(AuditLog.action == action.value)
    q = q.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    rows = db.scalars(q).all()
    out: list[AuditLogOut] = []
    for r in rows:
        detail = None
        if r.detail_json:
            try:
                detail = json.loads(r.detail_json)
                if not isinstance(detail, dict):
                    detail = {"_raw": r.detail_json}
            except json.JSONDecodeError:
                detail = {"_raw": r.detail_json}
        out.append(
            AuditLogOut(
                id=r.id,
                actor_user_id=r.actor_user_id,
                action=r.action,
                target_user_id=r.target_user_id,
                detail=detail,
                request_id=r.request_id,
                ip_address=r.ip_address,
                created_at=r.created_at,
            )
        )
    return out


@router.get("/students", response_model=list[StudentOverviewOut])
def list_students(
    admin: AdminUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(200, ge=1, le=500, description="Maximo de registos por pagina"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginacao"),
) -> list[StudentOverviewOut]:
    del admin
    users = db.scalars(select(User).order_by(User.id).limit(limit).offset(offset)).all()
    out: list[StudentOverviewOut] = []
    for u in users:
        cert = db.scalars(select(Certificate).where(Certificate.user_id == u.id)).first()
        completed = sorted(user_completed_set(db, u.id))
        sessions = count_active_refresh_tokens(db, u.id)
        out.append(
            StudentOverviewOut(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                created_at=u.created_at,
                completed_modules=completed,
                has_certificate=cert is not None,
                certificate_serial=cert.serial_number if cert else None,
                active_sessions=sessions,
            )
        )
    return out


@router.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(
    admin: AdminUser,
    body: AdminCreateStudentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    if db.scalars(select(User).where(User.email == body.email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email ja existe (duplicidade bloqueada)")
    try:
        validate_password_strength(body.password)
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(e)) from e
    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=UserRole.student,
    )
    db.add(user)
    db.flush()
    record_audit_log(
        db,
        actor_user_id=admin.id,
        action=AuditAction.STUDENT_CREATED,
        target_user_id=user.id,
        detail={"email": user.email},
        request=request,
    )
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/modules", status_code=status.HTTP_201_CREATED)
def upsert_module(
    admin: AdminUser,
    body: ModuleCreateIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    ct = encrypt_content(body.body_markdown)
    existing = db.scalars(select(CourseModule).where(CourseModule.slug == body.slug)).first()
    if existing:
        existing.title = body.title
        existing.ciphertext = ct
        record_audit_log(
            db,
            actor_user_id=admin.id,
            action=AuditAction.MODULE_UPSERTED,
            detail={"slug": body.slug, "updated": True},
            request=request,
        )
        db.commit()
        return {"slug": body.slug, "updated": True}
    row = CourseModule(slug=body.slug, title=body.title, ciphertext=ct)
    db.add(row)
    record_audit_log(
        db,
        actor_user_id=admin.id,
        action=AuditAction.MODULE_UPSERTED,
        detail={"slug": body.slug, "updated": False},
        request=request,
    )
    db.commit()
    return {"slug": body.slug, "updated": False}


@router.post("/modules/sync-from-curriculum", status_code=status.HTTP_201_CREATED)
def sync_modules_from_curriculum(
    admin: AdminUser,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Cria modulos em falta (conteudo placeholder encriptado) para cada id do curriculum.json."""
    slugs = load_required_module_slugs(settings.curriculum_json_path)
    created = 0
    placeholder = encrypt_content("_Conteudo em preparacao. O administrador pode atualizar este modulo._\n")
    with settings.curriculum_json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    titles = {str(n["id"]): n.get("title", n["id"]) for n in data["nodes"] if isinstance(n, dict)}
    for slug in slugs:
        if db.scalars(select(CourseModule).where(CourseModule.slug == slug)).first():
            continue
        db.add(
            CourseModule(
                slug=slug,
                title=str(titles.get(slug, slug)),
                ciphertext=placeholder,
            )
        )
        created += 1
    record_audit_log(
        db,
        actor_user_id=admin.id,
        action=AuditAction.CURRICULUM_SYNCED,
        detail={"created": created, "total_required": len(slugs)},
        request=request,
    )
    db.commit()
    return {"created": created, "total_required": len(slugs)}


@router.post("/students/{user_id}/revoke-sessions", response_model=RevokeSessionsOut)
def revoke_user_sessions(
    admin: AdminUser,
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> RevokeSessionsOut:
    """Revoga todos os refresh tokens do utilizador (logout em todos os dispositivos com sessao renovavel)."""
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilizador inexistente")
    n = revoke_all_user_refresh_tokens(db, user_id)
    record_audit_log(
        db,
        actor_user_id=admin.id,
        action=AuditAction.SESSIONS_REVOKED,
        target_user_id=user_id,
        detail={"revoked_count": n},
        request=request,
    )
    db.commit()
    return RevokeSessionsOut(user_id=user_id, revoked_count=n)


@router.patch("/students/{user_id}")
def patch_student(
    admin: AdminUser,
    user_id: int,
    body: AdminPatchStudentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilizador inexistente")
    patched: list[str] = []
    if body.full_name is not None:
        u.full_name = body.full_name
        patched.append("full_name")
    if body.is_active is not None:
        u.is_active = body.is_active
        patched.append("is_active")
    if patched:
        record_audit_log(
            db,
            actor_user_id=admin.id,
            action=AuditAction.STUDENT_UPDATED,
            target_user_id=user_id,
            detail={"fields": patched},
            request=request,
        )
    db.commit()
    return {"id": u.id, "email": u.email, "full_name": u.full_name, "is_active": u.is_active}


@router.get("/students/{user_id}/certificate-pdf")
def download_student_certificate(
    admin: AdminUser,
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    cert = db.scalars(select(Certificate).where(Certificate.user_id == user_id)).first()
    if not cert or not cert.pdf_blob:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sem certificado")
    record_audit_log(
        db,
        actor_user_id=admin.id,
        action=AuditAction.CERTIFICATE_PDF_DOWNLOADED,
        target_user_id=user_id,
        detail={"serial_number": cert.serial_number},
        request=request,
    )
    db.commit()
    from fastapi.responses import Response

    return Response(
        content=cert.pdf_blob,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificado-{cert.serial_number}.pdf"'
        },
    )
