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
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


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
    user = db.scalars(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou palavra-passe incorretos")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Conta desativada")
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
