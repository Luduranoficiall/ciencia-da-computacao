from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import CourseModule, StudentAssistantUsage
from app.security import decrypt_content


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def consume_daily_quota(db: Session, user_id: int) -> int:
    """Incrementa quota do dia e devolve uso restante."""
    d = _today_utc()
    row = db.scalars(
        select(StudentAssistantUsage).where(
            StudentAssistantUsage.user_id == user_id,
            StudentAssistantUsage.usage_date == d,
        )
    ).first()
    if not row:
        row = StudentAssistantUsage(user_id=user_id, usage_date=d, request_count=0)
        db.add(row)
        db.flush()
    row.request_count = int(row.request_count or 0) + 1
    if row.request_count > settings.assistant_daily_limit_per_user:
        raise ValueError("Limite diario do assistente atingido para hoje.")
    db.commit()
    return max(0, settings.assistant_daily_limit_per_user - row.request_count)


def build_local_assistant_answer(db: Session, module_slug: str, question: str) -> str:
    """Fallback local sem LLM: devolve contexto resumido do modulo."""
    mod = db.scalars(select(CourseModule).where(CourseModule.slug == module_slug)).first()
    if not mod:
        raise KeyError(module_slug)
    body = decrypt_content(mod.ciphertext)
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    preview = " ".join(lines[:5])[:600]
    q = question.strip()
    return (
        f"Pergunta: {q}\n\n"
        f"Resumo do modulo '{mod.title}': {preview or 'Sem conteudo textual suficiente.'}\n\n"
        "Passos sugeridos:\n"
        "- Releia o modulo e destaque 3 conceitos-chave.\n"
        "- Escreva um exemplo pratico aplicado a sua pergunta.\n"
        "- Teste o exemplo e compare com os objetivos da disciplina."
    )
