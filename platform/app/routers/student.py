from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import CurrentUser
from app.models import Certificate, CourseModule, StudentProgress, UserRole
from app.schemas import CertificateStatusOut, ModuleContentOut, ModuleListOut, ProgressOut
from app.services import (
    get_module_plain,
    issue_certificate_if_needed,
    is_fully_complete,
    required_slugs,
    user_completed_set,
)

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/modules", response_model=list[ModuleListOut])
def list_modules(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[ModuleListOut]:
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Use rotas admin para gestao")
    req = required_slugs(db)
    rows = db.scalars(select(CourseModule)).all()
    by_slug = {r.slug: r.title for r in rows}
    # Mantem a ordem do curriculum.json
    return [ModuleListOut(slug=s, title=by_slug[s]) for s in req if s in by_slug]


@router.get("/modules/{slug}/content", response_model=ModuleContentOut)
def module_content(
    slug: str,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ModuleContentOut:
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Conteudo encriptado para percurso de aluno")
    if slug not in set(required_slugs(db)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Modulo inexistente")
    try:
        title, body = get_module_plain(db, slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Modulo inexistente") from e
    return ModuleContentOut(slug=slug, title=title, body_markdown=body)


@router.post("/progress/{slug}", response_model=ProgressOut)
def mark_progress(
    slug: str,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ProgressOut:
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Apenas alunos marcam progresso")
    if slug not in set(required_slugs(db)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Modulo inexistente")
    mod = db.scalars(select(CourseModule).where(CourseModule.slug == slug)).first()
    if not mod:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Modulo inexistente")
    existing = db.scalars(
        select(StudentProgress).where(
            StudentProgress.user_id == user.id,
            StudentProgress.module_slug == slug,
        )
    ).first()
    if existing:
        # Se o aluno acabou de preencher tudo (ou ja estava elegivel), garante emissao idempotente.
        issue_certificate_if_needed(db, user)
        return ProgressOut(module_slug=slug, completed_at=existing.completed_at)
    row = StudentProgress(user_id=user.id, module_slug=slug)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalars(
            select(StudentProgress).where(
                StudentProgress.user_id == user.id,
                StudentProgress.module_slug == slug,
            )
        ).first()
        if not existing:
            raise
        return ProgressOut(module_slug=slug, completed_at=existing.completed_at)
    db.refresh(row)
    # Ao completar o percurso, emite automaticamente o certificado (idempotente).
    issue_certificate_if_needed(db, user)
    return ProgressOut(module_slug=slug, completed_at=row.completed_at)


@router.get("/progress", response_model=list[str])
def my_progress(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[str]:
    if user.role == UserRole.admin:
        return []
    return sorted(user_completed_set(db, user.id))


@router.get("/certificate/status", response_model=CertificateStatusOut)
def certificate_status(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CertificateStatusOut:
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Certificado aplica-se a alunos")
    eligible, c, t = is_fully_complete(db, user.id)
    cert = db.scalars(select(Certificate).where(Certificate.user_id == user.id)).first()
    return CertificateStatusOut(
        eligible=eligible,
        completed=c,
        required=t,
        has_certificate=cert is not None,
        serial_number=cert.serial_number if cert else None,
        issued_at=cert.issued_at if cert else None,
    )


@router.post("/certificate/issue", response_model=CertificateStatusOut)
def issue_my_certificate(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CertificateStatusOut:
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Apenas alunos")
    cert = issue_certificate_if_needed(db, user)
    eligible, c, t = is_fully_complete(db, user.id)
    return CertificateStatusOut(
        eligible=eligible,
        completed=c,
        required=t,
        has_certificate=cert is not None,
        serial_number=cert.serial_number if cert else None,
        issued_at=cert.issued_at if cert else None,
    )


@router.get("/certificate/pdf")
def download_my_certificate(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Apenas alunos")
    cert = db.scalars(select(Certificate).where(Certificate.user_id == user.id)).first()
    if not cert or not cert.pdf_blob:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificado ainda nao emitido")
    return Response(
        content=cert.pdf_blob,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificado-{cert.serial_number}.pdf"'
        },
    )
