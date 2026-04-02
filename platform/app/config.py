from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cookie_samesite: str = "lax"

    database_url: str = "sqlite:///./data/lms.db"

    # Fernet (32 bytes url-safe base64). Gerar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    content_encryption_key: str = ""

    # Atras de reverse proxy confiavel: usar primeiro IP de X-Forwarded-For para rate limits / logs.
    # NUNCA ativar sem proxy que sobrescreva o cabecalho (spoofing).
    trusted_forwarded_for: bool = False

    # POST /student/assistant/ask: rejeitar corpos acima disto (Content-Length). 0 = sem limite extra.
    assistant_max_request_body_bytes: int = 65536

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
    # Bloqueio por utilizador apos falhas repetidas de login
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    # Password policy (alfa-num + simbolo)
    password_require_upper: bool = True
    password_require_lower: bool = True
    password_require_digit: bool = True
    password_require_symbol: bool = True
    # Personal Prof (assistente de estudo)
    assistant_daily_limit_per_user: int = 30
    # Pedidos por IP por minuto (janela 60s). 0 = desligado. Complementa a quota diaria por utilizador.
    assistant_rate_limit_per_minute_per_ip: int = 0
    # LLM opcional (API OpenAI-compatible: OpenAI, Azure OpenAI, Ollama com proxy, etc.)
    assistant_llm_enabled: bool = True
    assistant_openai_api_key: str = ""
    assistant_openai_base_url: str = "https://api.openai.com/v1"
    assistant_openai_model: str = "gpt-4o-mini"
    assistant_openai_timeout_seconds: float = 60.0

    @field_validator("content_encryption_key")
    @classmethod
    def validate_fernet_key_format(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            return ""
        try:
            Fernet(v.encode())
        except Exception as e:
            raise ValueError(
                "CONTENT_ENCRYPTION_KEY invalida: use Fernet.generate_key() (32 bytes url-safe base64)."
            ) from e
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret_len(cls, v: str) -> str:
        # Evita warnings e fraqueza trivial em HS256 (recomendacao minima ~32 bytes)
        if len(v) < 32:
            raise ValueError("JWT_SECRET deve ter pelo menos 32 caracteres (HS256).")
        return v

    @field_validator("cookie_samesite")
    @classmethod
    def validate_cookie_samesite(cls, v: str) -> str:
        low = v.lower().strip()
        if low not in {"lax", "strict", "none"}:
            raise ValueError("COOKIE_SAMESITE deve ser lax, strict ou none.")
        return low


settings = Settings()
