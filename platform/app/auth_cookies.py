from fastapi.responses import JSONResponse

from app.config import settings


def attach_auth_cookies(response: JSONResponse, access: str, refresh: str) -> None:
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax",
        secure=settings.require_https,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 86400,
        samesite="lax",
        secure=settings.require_https,
        path="/auth",
    )


def clear_auth_cookies(response: JSONResponse) -> None:
    response.delete_cookie(settings.access_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/auth")
