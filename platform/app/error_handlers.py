"""Handlers de erro: respostas JSON consistentes e sem fugas em producao."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings

_log = logging.getLogger("app.error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, (HTTPException, RequestValidationError)):
            raise exc
        rid = getattr(request.state, "request_id", None)
        _log.error(
            "unhandled_exception request_id=%s path=%s",
            rid,
            request.url.path,
            exc_info=exc,
        )
        detail = str(exc) if settings.expose_internal_errors else "Erro interno do servidor."
        return JSONResponse(
            status_code=500,
            content={"detail": detail, "request_id": rid},
        )
