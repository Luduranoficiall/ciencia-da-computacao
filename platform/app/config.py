from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jwt_secret: str = "change-me-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    # Access JWT curto; sessao longa via refresh token (cookie HttpOnly + BD).
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Cookies HttpOnly (UI em mesmo site ou CORS explicito com credentials)
    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"

    database_url: str = "sqlite:///./data/lms.db"

    # Fernet (32 bytes url-safe base64). Gerar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    content_encryption_key: str = ""

    # Caminho para data/curriculum.json (IDs obrigatorios para conclusao)
    curriculum_json_path: Path = Path(__file__).resolve().parents[2] / "data" / "curriculum.json"

    # Textos da landing pública (validados no CI com JSON Schema)
    course_presentation_json_path: Path = (
        Path(__file__).resolve().parents[2] / "data" / "course_presentation.json"
    )

    # Se true, apenas admin cria contas (POST /admin/students)
    admin_only_registration: bool = True

    course_display_name: str = "Ciencia da Computacao (curriculo integrado)"

    # Opcional: cria admin no arranque se ainda nao existir (producao: preferir migracao manual)
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""

    # Origens CORS separadas por virgula (ex.: https://app.teudominio.pt). * para desenvolvimento.
    cors_origins: str = "*"

    # Hardening de producao: forcar HTTPS e cabecalhos de seguranca
    require_https: bool = False
    hsts_max_age_seconds: int = 63072000  # 2 anos

    # Hosts permitidos (Host header). Vazio = desligado. Ex.: "meudominio.pt,www.meudominio.pt"
    trusted_hosts: str = ""

    # Limite de tentativas de login por IP por minuto (0 = desligado)
    rate_limit_auth_per_minute: int = 30

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret_len(cls, v: str) -> str:
        # Evita warnings e fraqueza trivial em HS256 (recomendacao minima ~32 bytes)
        if len(v) < 32:
            raise ValueError("JWT_SECRET deve ter pelo menos 32 caracteres (HS256).")
        return v


settings = Settings()
