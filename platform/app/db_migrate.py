"""Migracoes leves para SQLite (sem Alembic) — colunas/tabelas em falta."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _ensure_audit_log_table(engine: Engine) -> None:
    if not str(engine.url).startswith("sqlite"):
        return
    insp = inspect(engine)
    if insp.has_table("audit_log"):
        return
    if not insp.has_table("users"):
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE audit_log (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    actor_user_id INTEGER NOT NULL,
                    action VARCHAR(128) NOT NULL,
                    target_user_id INTEGER,
                    detail_json TEXT,
                    request_id VARCHAR(64),
                    ip_address VARCHAR(45),
                    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                    FOREIGN KEY(actor_user_id) REFERENCES users (id),
                    FOREIGN KEY(target_user_id) REFERENCES users (id)
                )
                """
            )
        )
        conn.execute(text("CREATE INDEX ix_audit_log_actor_user_id ON audit_log (actor_user_id)"))
        conn.execute(text("CREATE INDEX ix_audit_log_action ON audit_log (action)"))
        conn.execute(text("CREATE INDEX ix_audit_log_target_user_id ON audit_log (target_user_id)"))


def ensure_sqlite_schema(engine: Engine) -> None:
    """Migracoes leves para SQLite (sem Alembic) — colunas/tabelas em falta."""
    if not str(engine.url).startswith("sqlite"):
        return
    _ensure_users_access_token_version(engine)
    _ensure_audit_log_table(engine)


def _ensure_users_access_token_version(engine: Engine) -> None:
    insp = inspect(engine)
    if not insp.has_table("users"):
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "access_token_version" in cols:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN access_token_version INTEGER NOT NULL DEFAULT 0"
            )
        )
