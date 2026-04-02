from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_cookies import attach_auth_cookies, clear_auth_cookies
from app.config import settings
from app.database import get_db
from app.models import User, UserRole
from app.refresh_token_service import create_refresh_token_row, revoke_refresh_token, rotate_refresh_token
from app.schemas import OkOut, RefreshIn, RegisterIn, TokenOut
from app.security import (
    create_access_token,
    hash_password,
    maybe_rehash_password_after_verify,
    validate_password_strength,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _json_token_response(access: str, refresh: str) -> JSONResponse:
    body = TokenOut(access_token=access, token_type="bearer").model_dump()
    resp = JSONResponse(content=body)
    attach_auth_cookies(resp, access, refresh)
    return resp


@router.post("/token", response_model=TokenOut)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> JSONResponse:
    now = datetime.now(timezone.utc)
    user = db.scalars(select(User).where(User.email == form.username)).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou palavra-passe incorretos")
    locked_until = _as_utc(user.locked_until)
    if locked_until and locked_until > now:
        raise HTTPException(
            status.HTTP_423_LOCKED,
            f"Conta temporariamente bloqueada. Tente novamente apos {locked_until.isoformat()}",
        )
    if not verify_password(form.password, user.hashed_password):
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= settings.max_failed_logins:
            user.locked_until = now + timedelta(minutes=settings.lockout_minutes)
            user.failed_login_attempts = 0
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou palavra-passe incorretos")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Conta desativada")
    user.failed_login_attempts = 0
    user.locked_until = None
    new_hash = maybe_rehash_password_after_verify(form.password, user.hashed_password)
    if new_hash:
        user.hashed_password = new_hash
    access = create_access_token(
        sub=user.email,
        role=user.role.value,
        user_id=user.id,
        token_version=user.access_token_version,
    )
    refresh = create_refresh_token_row(db, user.id)
    db.commit()
    return _json_token_response(access, refresh)


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Annotated[Session, Depends(get_db)]) -> JSONResponse:
    if settings.admin_only_registration:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Registo publico desligado. Peça acesso ao administrador.",
        )
    if db.scalars(select(User).where(User.email == body.email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email ja registado")
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
    db.commit()
    db.refresh(user)
    access = create_access_token(
        sub=user.email,
        role=user.role.value,
        user_id=user.id,
        token_version=user.access_token_version,
    )
    refresh = create_refresh_token_row(db, user.id)
    db.commit()
    return _json_token_response(access, refresh)


@router.post("/refresh", response_model=TokenOut)
def refresh_tokens(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    body: RefreshIn | None = None,
) -> JSONResponse:
    raw = request.cookies.get(settings.refresh_cookie_name) or (body.refresh_token if body else None)
    if not raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token em falta (cookie ou corpo)")
    try:
        access, new_refresh = rotate_refresh_token(db, raw)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
    return _json_token_response(access, new_refresh)


@router.post("/logout", response_model=OkOut)
def logout(request: Request, db: Annotated[Session, Depends(get_db)]) -> JSONResponse:
    raw = request.cookies.get(settings.refresh_cookie_name)
    if raw:
        revoke_refresh_token(db, raw)
    resp = JSONResponse(content=OkOut().model_dump())
    clear_auth_cookies(resp)
    return resp
