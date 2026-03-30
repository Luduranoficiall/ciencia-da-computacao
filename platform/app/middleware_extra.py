"""Middlewares auxiliares: request id, rate limit no login, cabecalhos de seguranca."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

# IP -> timestamps monotonicos (ultimos 60s)
_auth_hits: dict[str, list[float]] = defaultdict(list)
_AUTH_WINDOW_S = 60.0


def _client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _prune_and_count(ip: str, max_per_window: int) -> bool:
    """True se permitido, False se excedeu."""
    now = time.monotonic()
    hits = _auth_hits[ip]
    while hits and (now - hits[0]) > _AUTH_WINDOW_S:
        hits.pop(0)
    if len(hits) >= max_per_window:
        return False
    hits.append(now)
    return True


class RequestIdAndSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid

        if (
            request.method == "POST"
            and request.url.path == "/auth/token"
            and settings.rate_limit_auth_per_minute > 0
        ):
            ip = _client_ip(request)
            if not _prune_and_count(ip, settings.rate_limit_auth_per_minute):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Muitas tentativas de login. Tente novamente em alguns minutos.",
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

        return resp
