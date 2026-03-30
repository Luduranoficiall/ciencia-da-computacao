import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.course_presentation_load import load_course_presentation
from app.database import get_db
from app.models import Certificate
from app.schemas import PublicCertificateVerifyOut

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/course-presentation")
def get_course_presentation() -> dict[str, Any]:
    """Textos da oferta formativa e alinhamento com a plataforma (sem autenticação)."""
    try:
        return load_course_presentation(settings.course_presentation_json_path)
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Ficheiro course_presentation.json indisponivel",
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            f"JSON invalido em course_presentation: {e}",
        )


@router.get("/certificates/verify/{serial}", response_model=PublicCertificateVerifyOut)
def verify_certificate(
    serial: Annotated[
        str,
        Path(
            min_length=1,
            max_length=64,
            pattern=r"^[A-Za-z0-9_-]+$",
            description="Serial do certificado (apenas letras, numeros, _ e -)",
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> PublicCertificateVerifyOut:
    cert = db.scalars(select(Certificate).where(Certificate.serial_number == serial)).first()
    if not cert:
        return PublicCertificateVerifyOut(serial_number=serial, valid=False, issued_at=None)
    return PublicCertificateVerifyOut(
        serial_number=serial,
        valid=True,
        issued_at=cert.issued_at,
    )

