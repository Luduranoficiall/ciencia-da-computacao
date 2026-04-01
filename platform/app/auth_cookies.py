from fastapi.responses import JSONResponse

from app.config import settings


def attach_auth_cookies(response: JSONResponse, access: str, refresh: str) -> None:
    secure_cookie = settings.require_https or settings.cookie_samesite == "none"
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite=settings.cookie_samesite,
        secure=secure_cookie,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 86400,
        samesite=settings.cookie_samesite,
        secure=secure_cookie,
        path="/auth",
    )


def clear_auth_cookies(response: JSONResponse) -> None:
    response.delete_cookie(settings.access_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/auth")
