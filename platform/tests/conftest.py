from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_rate_limit_buckets():
    from app.middleware_extra import reset_rate_limit_buckets_for_tests

    reset_rate_limit_buckets_for_tests()
    yield


@pytest.fixture
def tmp_curriculum(tmp_path: Path) -> Path:
    p = tmp_path / "curriculum.json"
    p.write_text(
        '{"nodes":['
        '{"id":"m1","title":"Modulo 1"},'
        '{"id":"m2","title":"Modulo 2"}'
        "]}",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def client(tmp_path: Path, tmp_curriculum: Path, monkeypatch: pytest.MonkeyPatch):
    from app import config
    from app.database import Base, get_engine, reset_engine_for_tests
    from app.db_migrate import ensure_sqlite_schema

    reset_engine_for_tests()
    db_file = tmp_path / "test.db"
    config.settings.database_url = f"sqlite:///{db_file}"
    config.settings.content_encryption_key = Fernet.generate_key().decode()
    config.settings.curriculum_json_path = tmp_curriculum
    config.settings.jwt_secret = "test-jwt-secret-key-exactly-32b!"
    config.settings.bootstrap_admin_email = ""
    config.settings.bootstrap_admin_password = ""
    config.settings.admin_only_registration = True
    config.settings.rate_limit_auth_per_minute = 0
    config.settings.trusted_hosts = ""

    eng = get_engine()
    Base.metadata.create_all(bind=eng)
    ensure_sqlite_schema(eng)

    from app.main import app

    return TestClient(app)
