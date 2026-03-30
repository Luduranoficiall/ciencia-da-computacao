from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, UserRole
from app.security import decode_token

security_bearer = HTTPBearer(auto_error=False)


def get_access_token_from_bearer_or_cookie(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
) -> str:
    if creds and creds.credentials:
        return creds.credentials.strip()
    cookie_token = request.cookies.get(settings.access_cookie_name)
    if cookie_token:
        return cookie_token.strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token em falta (Authorization: Bearer ou cookie HttpOnly)",
    )


def get_current_user(
    token: Annotated[str, Depends(get_access_token_from_bearer_or_cookie)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
        ) from exc
    uid = payload.get("uid")
    if uid is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token sem utilizador")
    user = db.get(User, int(uid))
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilizador inativo ou inexistente")
    tv_claim = payload.get("tv")
    try:
        tv = int(tv_claim) if tv_claim is not None else 0
    except (TypeError, ValueError):
        tv = 0
    if user.access_token_version != tv:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Token revogado ou sessao invalidada pelo administrador",
        )
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Apenas administrador")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
