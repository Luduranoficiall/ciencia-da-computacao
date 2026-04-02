from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.assistant_service import assistant_llm_configured
from app.config import settings
from app.database import Base, get_engine, get_session_factory
from app.db_migrate import ensure_sqlite_schema
from app.middleware_extra import LimitRequestBodyMiddleware, RequestIdAndSecurityMiddleware
from app.models import User, UserRole
from app.routers import admin, auth, public, student
from app.security import hash_password

logging.basicConfig(level=logging.INFO, format="%(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    eng = get_engine()
    Base.metadata.create_all(bind=eng)
    ensure_sqlite_schema(eng)
    if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
        db = get_session_factory()()
        try:
            exists = db.scalars(select(User).where(User.email == settings.bootstrap_admin_email)).first()
            if not exists:
                db.add(
                    User(
                        email=settings.bootstrap_admin_email,
                        full_name="Administrador",
                        hashed_password=hash_password(settings.bootstrap_admin_password),
                        role=UserRole.admin,
                    )
                )
                db.commit()
        finally:
            db.close()
    yield


app = FastAPI(
    title="Plataforma curso (ciencia-da-computacao)",
    description="API com conteudo encriptado, progresso, certificado e visao global apenas para admin.",
    lifespan=lifespan,
)

_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()] or ["*"]
# Com allow_credentials=True o browser nao aceita *. Use origens explicitas para SPA noutro dominio.
_cors_credentials = _cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.require_https:
    app.add_middleware(HTTPSRedirectMiddleware)

_hosts = [h.strip() for h in settings.trusted_hosts.split(",") if h.strip()]
if _hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=_hosts)

# Rate limit + request id + headers; depois limite de corpo (ultimo = executa primeiro no pedido)
app.add_middleware(RequestIdAndSecurityMiddleware)
app.add_middleware(LimitRequestBodyMiddleware)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(student.router)
app.include_router(public.router)

# Interface web/PWA do aluno (sem dependencias extra: HTML/JS/SPA)
static_dir = Path(__file__).resolve().parents[1] / "static"
if static_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

# RFC 9116 — substituir Contact antes de producao
_SECURITY_TXT = """# Editar Contact antes de deploy publico.
Contact: mailto:security@example.com
Preferred-Languages: pt, en
"""


@app.get("/.well-known/security.txt", include_in_schema=False)
def security_txt() -> Response:
    return Response(
        content=_SECURITY_TXT.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


def _assistant_health() -> dict:
    return {"llm_configured": assistant_llm_configured()}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "assistant": _assistant_health()}


@app.get("/health/ready")
def health_ready() -> dict:
    """Verifica ligacao a BD (para orquestradores / load balancers)."""
    a = _assistant_health()
    try:
        db = get_session_factory()()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "not_ready",
            "database": "error",
            "detail": str(e),
            "assistant": a,
        }
    return {"status": "ok", "database": "ok", "assistant": a}
