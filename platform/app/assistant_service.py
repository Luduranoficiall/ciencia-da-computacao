from __future__ import annotations

from datetime import datetime, timezone

import httpx
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


def _local_from_plain(title: str, body_plain: str, question: str) -> str:
    lines = [ln.strip() for ln in body_plain.splitlines() if ln.strip()]
    preview = " ".join(lines[:5])[:600]
    q = question.strip()
    return (
        f"Pergunta: {q}\n\n"
        f"Resumo do modulo '{title}': {preview or 'Sem conteudo textual suficiente.'}\n\n"
        "Passos sugeridos:\n"
        "- Releia o modulo e destaque 3 conceitos-chave.\n"
        "- Escreva um exemplo pratico aplicado a sua pergunta.\n"
        "- Teste o exemplo e compare com os objetivos da disciplina."
    )


def _openai_compatible_chat(title: str, body_plain: str, question: str) -> str:
    key = (settings.assistant_openai_api_key or "").strip()
    if not key:
        raise ValueError("API key em falta")
    base = settings.assistant_openai_base_url.rstrip("/")
    url = f"{base}/chat/completions"
    # Limita contexto para evitar custos excessivos
    max_chars = 12000
    ctx = body_plain[:max_chars]
    payload = {
        "model": settings.assistant_openai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Es um tutor de Ciencia da Computacao. Responde em portugues (PT-PT ou PT-BR), "
                    "de forma clara e pedagogica. Usa apenas o contexto fornecido do modulo; "
                    "se nao houver informacao suficiente, indica isso explicitamente."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Titulo do modulo: {title}\n\n"
                    f"Conteudo do modulo (Markdown ou texto):\n{ctx}\n\n"
                    f"Pergunta do aluno:\n{question.strip()}"
                ),
            },
        ],
        "temperature": 0.35,
        "max_tokens": 1200,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    timeout = float(settings.assistant_openai_timeout_seconds)
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("Resposta LLM sem choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Resposta LLM vazia")
    return content.strip()


def build_assistant_answer(db: Session, module_slug: str, question: str) -> str:
    """Tenta LLM (OpenAI-compatible) se configurado; caso contrario ou em falha, usa modo local."""
    mod = db.scalars(select(CourseModule).where(CourseModule.slug == module_slug)).first()
    if not mod:
        raise KeyError(module_slug)
    body_plain = decrypt_content(mod.ciphertext)
    use_llm = (
        settings.assistant_llm_enabled
        and (settings.assistant_openai_api_key or "").strip() != ""
    )
    if use_llm:
        try:
            return _openai_compatible_chat(mod.title, body_plain, question)
        except Exception:
            pass
    return _local_from_plain(mod.title, body_plain, question)


def build_local_assistant_answer(db: Session, module_slug: str, question: str) -> str:
    """Fallback local explicito (testes e compatibilidade)."""
    mod = db.scalars(select(CourseModule).where(CourseModule.slug == module_slug)).first()
    if not mod:
        raise KeyError(module_slug)
    body_plain = decrypt_content(mod.ciphertext)
    return _local_from_plain(mod.title, body_plain, question)
