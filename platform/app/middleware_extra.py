"""Middlewares auxiliares: request id, rate limit no login, cabecalhos de seguranca."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

# IP -> timestamps monotonicos (ultimos 60s)
_auth_hits: dict[str, list[float]] = defaultdict(list)
_assistant_hits: dict[str, list[float]] = defaultdict(list)
_AUTH_WINDOW_S = 60.0
_log = logging.getLogger("app.request")


def reset_rate_limit_buckets_for_tests() -> None:
    """Limpa contadores in-memory (apenas para testes)."""
    _auth_hits.clear()
    _assistant_hits.clear()


def _client_ip(request: Request) -> str:
    if settings.trusted_forwarded_for:
        fwd = (request.headers.get("x-forwarded-for") or "").strip()
        if fwd:
            first = fwd.split(",")[0].strip()
            if first:
                return first
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _prune_and_count(bucket: dict[str, list[float]], key: str, max_per_window: int) -> bool:
    """True se permitido, False se excedeu (janela deslizante de _AUTH_WINDOW_S)."""
    now = time.monotonic()
    hits = bucket[key]
    while hits and (now - hits[0]) > _AUTH_WINDOW_S:
        hits.pop(0)
    if len(hits) >= max_per_window:
        return False
    hits.append(now)
    return True


class RequestIdAndSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.monotonic()
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid

        if (
            request.method == "POST"
            and request.url.path == "/auth/token"
            and settings.rate_limit_auth_per_minute > 0
        ):
            ip = _client_ip(request)
            if not _prune_and_count(_auth_hits, ip, settings.rate_limit_auth_per_minute):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Muitas tentativas de login. Tente novamente em alguns minutos.",
                    },
                    headers={"Retry-After": "60", "X-Request-ID": rid},
                )

        if (
            request.method == "POST"
            and request.url.path == "/student/assistant/ask"
            and settings.assistant_rate_limit_per_minute_per_ip > 0
        ):
            ip = _client_ip(request)
            if not _prune_and_count(
                _assistant_hits, ip, settings.assistant_rate_limit_per_minute_per_ip
            ):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Muitas perguntas ao assistente a partir deste IP. Tente novamente em breve.",
                    },
                    headers={"Retry-After": "60", "X-Request-ID": rid},
                )

        resp: Response = await call_next(request)

        resp.headers["X-Request-ID"] = rid
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=()"

        p = request.url.path
        if p.startswith("/student/") or p.startswith("/auth/"):
            resp.headers["Cache-Control"] = "private, no-store"

        if p.startswith("/ui"):
            resp.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self'; "
                "worker-src 'self'; "
                "manifest-src 'self'"
            )

        if settings.require_https:
            resp.headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age_seconds}; includeSubDomains"
            )

        elapsed_ms = int((time.monotonic() - t0) * 1000)
        _log.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": rid,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": resp.status_code,
                    "elapsed_ms": elapsed_ms,
                    "client_ip": _client_ip(request),
                },
                ensure_ascii=True,
            )
        )

        return resp


class LimitRequestBodyMiddleware(BaseHTTPMiddleware):
    """Rejeita pedidos JSON demasiado grandes antes de processar (ex.: assistente)."""

    async def dispatch(self, request: Request, call_next):
        max_b = int(settings.assistant_max_request_body_bytes or 0)
        if (
            max_b > 0
            and request.method == "POST"
            and request.url.path == "/student/assistant/ask"
        ):
            cl = request.headers.get("content-length")
            if cl:
                try:
                    if int(cl) > max_b:
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Corpo do pedido demasiado grande."},
                        )
                except ValueError:
                    pass
        return await call_next(request)
