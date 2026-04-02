import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.database import get_session_factory
from app.models import CourseModule, User, UserRole
from app.security import encrypt_content, hash_password


def _admin_token(c) -> str:
    r = c.post(
        "/auth/token",
        data={"username": "admin@test.local", "password": "adminpass12"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _student_token(c) -> str:
    r = c.post(
        "/auth/token",
        data={"username": "stu@test.local", "password": "studentpass12"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_admin_sees_all_students(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno Um",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    tok = _admin_token(client)
    r = client.get("/admin/students", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    emails = {x["email"] for x in data}
    assert emails == {"admin@test.local", "stu@test.local"}


def test_progress_idempotent_and_certificate_once(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Maria Silva",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    from sqlalchemy import select

    db.commit()
    stu = db.scalars(select(User).where(User.email == "stu@test.local")).first()
    for slug, title in [("m1", "M1"), ("m2", "M2")]:
        db.add(
            CourseModule(
                slug=slug,
                title=title,
                ciphertext=encrypt_content(f"# {title}\nConteudo."),
            )
        )
    db.commit()
    sid = stu.id
    db.close()

    st = _student_token(client)
    h = {"Authorization": f"Bearer {st}"}

    r1 = client.post("/student/progress/m1", headers=h)
    r2 = client.post("/student/progress/m1", headers=h)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["module_slug"] == r2.json()["module_slug"]

    client.post("/student/progress/m2", headers=h)

    s = client.get("/student/certificate/status", headers=h).json()
    assert s["eligible"] is True
    assert s["has_certificate"] is True

    client.post("/student/certificate/issue", headers=h)
    client.post("/student/certificate/issue", headers=h)

    db = get_session_factory()()
    from sqlalchemy import select
    from app.models import Certificate

    certs = db.scalars(select(Certificate).where(Certificate.user_id == sid)).all()
    assert len(certs) == 1
    serial = certs[0].serial_number
    db.close()

    pdf = client.get("/student/certificate/pdf", headers=h)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"

    # Verificacao publica por serial (sem dados pessoais)
    v = client.get(f"/public/certificates/verify/{serial}").json()
    assert v["serial_number"] == serial
    assert v["valid"] is True

    v2 = client.get("/public/certificates/verify/serial-nao-existe").json()
    assert v2["valid"] is False


def test_public_verify_rejects_invalid_serial(client):
    r = client.get("/public/certificates/verify/foo@bar")
    assert r.status_code == 422


def test_health_ready_ok(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    data = r.json()
    assert data.get("database") == "ok"
    assert data.get("assistant", {}).get("llm_configured") is False


def test_health_includes_assistant_llm_configured(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["assistant"]["llm_configured"] is False


def test_health_assistant_llm_configured_true_when_key_set(client, monkeypatch):
    from app import config

    monkeypatch.setattr(config.settings, "assistant_llm_enabled", True)
    monkeypatch.setattr(config.settings, "assistant_openai_api_key", "sk-test")
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["assistant"]["llm_configured"] is True


def test_security_txt_endpoint(client):
    r = client.get("/.well-known/security.txt")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")
    assert b"Contact:" in r.content


def test_login_upgrades_bcrypt_hash_to_argon2(client):
    import bcrypt
    from sqlalchemy import select

    db = get_session_factory()()
    legacy = bcrypt.hashpw(b"studentpass12", bcrypt.gensalt()).decode()
    db.add(
        User(
            email="legacy@test.local",
            full_name="Legado",
            hashed_password=legacy,
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    r = client.post(
        "/auth/token",
        data={"username": "legacy@test.local", "password": "studentpass12"},
    )
    assert r.status_code == 200, r.text
    db = get_session_factory()()
    u = db.scalars(select(User).where(User.email == "legacy@test.local")).first()
    assert u is not None
    assert u.hashed_password.startswith("$argon2")
    db.close()


def test_assistant_post_rejects_oversized_body(client, monkeypatch):
    from app import config

    monkeypatch.setattr(config.settings, "assistant_max_request_body_bytes", 80)
    body = b'{"module_slug":"m1","question":"' + b"x" * 200 + b'"}'
    r = client.post(
        "/student/assistant/ask",
        content=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
    )
    assert r.status_code == 413


def test_assistant_llm_configured_matches_settings(monkeypatch):
    from app import config
    from app.assistant_service import assistant_llm_configured

    monkeypatch.setattr(config.settings, "assistant_llm_enabled", True)
    monkeypatch.setattr(config.settings, "assistant_openai_api_key", "")
    assert assistant_llm_configured() is False
    monkeypatch.setattr(config.settings, "assistant_openai_api_key", "sk-x")
    assert assistant_llm_configured() is True
    monkeypatch.setattr(config.settings, "assistant_llm_enabled", False)
    assert assistant_llm_configured() is False


def test_openapi_assistant_schemas_have_examples(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schemas = r.json()["components"]["schemas"]
    for name in ("AssistantAskIn", "AssistantAskOut"):
        schema = schemas[name]
        assert "examples" in schema and isinstance(schema["examples"], list)
    ex_in = schemas["AssistantAskIn"]["examples"][0]
    assert ex_in.get("module_slug") and ex_in.get("question")
    ex_out = schemas["AssistantAskOut"]["examples"][0]
    assert ex_out.get("module_slug")
    assert isinstance(ex_out.get("answer"), str) and ex_out.get("answer")
    assert isinstance(ex_out.get("usage_remaining_today"), int)


def test_assistant_ask_structured_log_excludes_question_text(caplog, client):
    """Regressao: nao registar o texto da pergunta (PII / dados sensiveis)."""
    from app import config

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.add(
        CourseModule(
            slug="m1",
            title="Modulo 1",
            ciphertext=encrypt_content("Conteudo do modulo."),
        )
    )
    db.commit()
    db.close()
    config.settings.assistant_daily_limit_per_user = 10

    st = _student_token(client)
    secret_phrase = "texto-da-pergunta-que-nao-deve-ir-para-logs-xyz"
    with caplog.at_level(logging.INFO, logger="app.assistant"):
        r = client.post(
            "/student/assistant/ask",
            headers={"Authorization": f"Bearer {st}"},
            json={"module_slug": "m1", "question": secret_phrase},
        )
    assert r.status_code == 200
    payloads = []
    for rec in caplog.records:
        if rec.name != "app.assistant":
            continue
        payloads.append(json.loads(rec.message))
    assert payloads, "esperado pelo menos um log JSON do assistente"
    for p in payloads:
        assert "question" not in p
        assert secret_phrase not in json.dumps(p)
        assert p.get("event") == "assistant_ask"
        assert p.get("mode") in ("llm", "local")
        assert p.get("module_slug") == "m1"
        assert "user_id" in p


def test_cookie_auth_and_refresh(client):
    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    r = client.post(
        "/auth/token",
        data={"username": "stu@test.local", "password": "studentpass12"},
    )
    assert r.status_code == 200
    assert r.json().get("access_token")

    r2 = client.get("/student/modules")
    assert r2.status_code == 200

    r3 = client.post("/auth/refresh")
    assert r3.status_code == 200
    assert r3.json().get("access_token")

    r4 = client.post("/auth/logout")
    assert r4.status_code == 200
    r5 = client.get("/student/modules")
    assert r5.status_code == 401


def test_admin_revoke_all_student_sessions(client):
    """Admin revoga refresh tokens; aluno deixa de renovar sessao (POST /auth/refresh falha)."""
    from starlette.testclient import TestClient

    from app.main import app

    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    stu_client = TestClient(app)
    assert stu_client.post(
        "/auth/token",
        data={"username": "stu@test.local", "password": "studentpass12"},
    ).status_code == 200
    assert stu_client.get("/student/modules").status_code == 200

    tok = _admin_token(client)
    lst = client.get("/admin/students", headers={"Authorization": f"Bearer {tok}"}).json()
    stu_row = next(x for x in lst if x["email"] == "stu@test.local")
    assert stu_row["active_sessions"] >= 1
    uid = stu_row["id"]

    r = client.post(
        f"/admin/students/{uid}/revoke-sessions",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    assert r.json()["revoked_count"] >= 1
    assert r.json()["user_id"] == uid

    lst2 = client.get("/admin/students", headers={"Authorization": f"Bearer {tok}"}).json()
    stu2 = next(x for x in lst2 if x["email"] == "stu@test.local")
    assert stu2["active_sessions"] == 0

    assert stu_client.post("/auth/refresh").status_code == 401
    # Access JWT (cookie) tambem invalidado (claim `tv`)
    assert stu_client.get("/student/modules").status_code == 401


def test_audit_log_after_revoke_sessions(client):
    """POST revoke-sessions cria linha em audit_log; GET /admin/audit-log devolve contexto."""
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    adm = _admin_token(client)
    lst = client.get("/admin/students", headers={"Authorization": f"Bearer {adm}"}).json()
    admin_id = next(x["id"] for x in lst if x["email"] == "admin@test.local")
    uid = next(x["id"] for x in lst if x["email"] == "stu@test.local")

    r = client.post(
        f"/admin/students/{uid}/revoke-sessions",
        headers={"Authorization": f"Bearer {adm}"},
    )
    assert r.status_code == 200

    logs = client.get("/admin/audit-log", headers={"Authorization": f"Bearer {adm}"}).json()
    assert len(logs) >= 1
    row = next(x for x in logs if x["action"] == "sessions_revoked")
    assert row["actor_user_id"] == admin_id
    assert row["target_user_id"] == uid
    assert row["detail"]["revoked_count"] >= 0


def test_audit_log_filter_rejects_unknown_action(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.commit()
    db.close()
    tok = _admin_token(client)
    r = client.get(
        "/admin/audit-log",
        params={"action": "not_a_registered_action"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 422


def test_audit_log_action_filter(client):
    """GET /admin/audit-log?action=... filtra pelo nome da acao."""
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.commit()
    db.close()

    tok = _admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    r = client.post(
        "/admin/students",
        headers=h,
        json={
            "email": "auditfilt@example.com",
                "password": "Longpassword1!",
            "full_name": "Novo",
        },
    )
    assert r.status_code == 201

    only_created = client.get("/admin/audit-log", params={"action": "student_created"}, headers=h).json()
    assert len(only_created) == 1
    assert only_created[0]["action"] == "student_created"
    assert only_created[0]["detail"]["email"] == "auditfilt@example.com"

    no_sessions = client.get(
        "/admin/audit-log", params={"action": "sessions_revoked"}, headers=h
    ).json()
    assert no_sessions == []


def test_patch_student_emits_audit(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    tok = _admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    uid = client.get("/admin/students", headers=h).json()
    uid = next(x["id"] for x in uid if x["email"] == "stu@test.local")

    assert (
        client.patch(
            f"/admin/students/{uid}",
            headers=h,
            json={"is_active": False},
        ).status_code
        == 200
    )

    rows = client.get(
        "/admin/audit-log", params={"action": "student_updated"}, headers=h
    ).json()
    assert len(rows) >= 1
    assert rows[0]["target_user_id"] == uid
    assert "is_active" in rows[0]["detail"]["fields"]


def test_public_course_presentation(client):
    r = client.get("/public/course-presentation")
    assert r.status_code == 200
    j = r.json()
    assert j.get("version") == 1
    assert "Ciência" in j.get("title", "")
    assert j.get("platform_alignment", {}).get("items")


def test_course_presentation_missing_returns_503(client, monkeypatch):
    from app import config

    monkeypatch.setattr(
        config.settings,
        "course_presentation_json_path",
        Path("/nonexistent/course_presentation.json"),
    )
    r = client.get("/public/course-presentation")
    assert r.status_code == 503


def test_admin_create_student_rejects_weak_password(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.commit()
    db.close()
    adm = _admin_token(client)
    r = client.post(
        "/admin/students",
        headers={"Authorization": f"Bearer {adm}"},
        json={"email": "weak@example.com", "password": "weakpass12", "full_name": "Weak"},
    )
    assert r.status_code == 422


def test_login_lockout_after_repeated_failures(client):
    from app import config

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    config.settings.max_failed_logins = 2
    config.settings.lockout_minutes = 1
    for _ in range(2):
        r = client.post(
            "/auth/token",
            data={"username": "stu@test.local", "password": "errada-123"},
        )
        assert r.status_code == 401
    r2 = client.post(
        "/auth/token",
        data={"username": "stu@test.local", "password": "studentpass12"},
    )
    assert r2.status_code == 423


def test_student_assistant_answer_and_quota(client):
    from app import config

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.add(
        CourseModule(
            slug="m1",
            title="Modulo 1",
            ciphertext=encrypt_content("Conceitos base do modulo 1\nExemplo pratico"),
        )
    )
    db.commit()
    db.close()
    config.settings.assistant_daily_limit_per_user = 2

    st = _student_token(client)
    h = {"Authorization": f"Bearer {st}"}
    r1 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Como estudar este modulo?"},
    )
    assert r1.status_code == 200
    assert "Resumo do modulo" in r1.json()["answer"]
    assert r1.json()["usage_remaining_today"] == 1

    r2 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Mais um resumo por favor."},
    )
    assert r2.status_code == 200
    r3 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Outra pergunta final."},
    )
    assert r3.status_code == 429


def test_student_assistant_uses_llm_when_key_configured(client, monkeypatch):
    from app import config

    monkeypatch.setattr(config.settings, "assistant_openai_api_key", "sk-test-key")
    monkeypatch.setattr(config.settings, "assistant_llm_enabled", True)
    monkeypatch.setattr(config.settings, "assistant_openai_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr(config.settings, "assistant_daily_limit_per_user", 10)

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.add(
        CourseModule(
            slug="m1",
            title="Modulo 1",
            ciphertext=encrypt_content("Conteudo do modulo para o LLM."),
        )
    )
    db.commit()
    db.close()

    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "Resposta sintetica do LLM."}}]}

    with patch("app.assistant_service.httpx.Client") as mc:
        mock_client = MagicMock()
        mock_client.post.return_value = FakeResp()
        mc.return_value.__enter__.return_value = mock_client

        st = _student_token(client)
        r = client.post(
            "/student/assistant/ask",
            headers={"Authorization": f"Bearer {st}"},
            json={"module_slug": "m1", "question": "Resuma o modulo em tres linhas."},
        )
        assert r.status_code == 200
        assert r.json()["answer"] == "Resposta sintetica do LLM."
        mock_client.post.assert_called_once()


def test_student_assistant_slug_not_in_curriculum_404(client):
    from app import config

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()
    config.settings.assistant_daily_limit_per_user = 5

    st = _student_token(client)
    r = client.post(
        "/student/assistant/ask",
        headers={"Authorization": f"Bearer {st}"},
        json={"module_slug": "zzz", "question": "Pergunta com mais de cinco caracteres."},
    )
    assert r.status_code == 404


def test_student_assistant_no_quota_consumed_when_module_row_missing(client):
    """Slug no curriculum mas sem linha em course_modules: 404 sem gastar quota."""
    from app import config

    config.settings.assistant_daily_limit_per_user = 10
    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.add(
        CourseModule(
            slug="m1",
            title="So M1",
            ciphertext=encrypt_content("Conteudo."),
        )
    )
    db.commit()
    db.close()

    st = _student_token(client)
    h = {"Authorization": f"Bearer {st}"}
    r0 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m2", "question": "Pergunta com texto suficiente aqui."},
    )
    assert r0.status_code == 404

    r1 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Primeira pergunta valida ao modulo."},
    )
    assert r1.status_code == 200
    assert r1.json()["usage_remaining_today"] == 9


def test_assistant_rate_limit_per_ip_returns_429(client, monkeypatch):
    from app import config

    monkeypatch.setattr(config.settings, "assistant_rate_limit_per_minute_per_ip", 2)
    monkeypatch.setattr(config.settings, "assistant_daily_limit_per_user", 10)

    db = get_session_factory()()
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.add(
        CourseModule(
            slug="m1",
            title="M1",
            ciphertext=encrypt_content("Conteudo do modulo."),
        )
    )
    db.commit()
    db.close()

    st = _student_token(client)
    h = {"Authorization": f"Bearer {st}"}
    r1 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Primeira pergunta com texto suficiente."},
    )
    assert r1.status_code == 200
    assert r1.json()["usage_remaining_today"] == 9

    r2 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Segunda pergunta com texto suficiente."},
    )
    assert r2.status_code == 200
    assert r2.json()["usage_remaining_today"] == 8

    r3 = client.post(
        "/student/assistant/ask",
        headers=h,
        json={"module_slug": "m1", "question": "Terceira pergunta deve ser bloqueada."},
    )
    assert r3.status_code == 429
    assert "IP" in r3.json()["detail"]


def test_student_cannot_list_audit_log(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()
    st = _student_token(client)
    r = client.get("/admin/audit-log", headers={"Authorization": f"Bearer {st}"})
    assert r.status_code == 403


def test_revoke_sessions_invalidates_bearer_access_token(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.add(
        User(
            email="stu@test.local",
            full_name="Aluno",
            hashed_password=hash_password("studentpass12"),
            role=UserRole.student,
        )
    )
    db.commit()
    db.close()

    st_tok = _student_token(client)
    h = {"Authorization": f"Bearer {st_tok}"}
    assert client.get("/student/modules", headers=h).status_code == 200

    adm = _admin_token(client)
    lst = client.get("/admin/students", headers={"Authorization": f"Bearer {adm}"}).json()
    uid = next(x["id"] for x in lst if x["email"] == "stu@test.local")

    assert (
        client.post(
            f"/admin/students/{uid}/revoke-sessions",
            headers={"Authorization": f"Bearer {adm}"},
        ).status_code
        == 200
    )

    assert client.get("/student/modules", headers=h).status_code == 401


def test_duplicate_email_blocked(client):
    db = get_session_factory()()
    db.add(
        User(
            email="admin@test.local",
            full_name="Admin",
            hashed_password=hash_password("adminpass12"),
            role=UserRole.admin,
        )
    )
    db.commit()
    db.close()
    tok = _admin_token(client)
    r = client.post(
        "/admin/students",
        headers={"Authorization": f"Bearer {tok}"},
        json={"email": "a@b.c", "password": "Longpassword1!", "full_name": "A"},
    )
    assert r.status_code == 201
    r2 = client.post(
        "/admin/students",
        headers={"Authorization": f"Bearer {tok}"},
        json={"email": "a@b.c", "password": "Otherpass12!", "full_name": "B"},
    )
    assert r2.status_code == 409


def test_curriculum_duplicate_ids_rejected(tmp_path):
    from app.curriculum_load import load_required_module_slugs

    bad = tmp_path / "bad.json"
    bad.write_text(
        '{"nodes":[{"id":"x","title":"1"},{"id":"x","title":"2"}]}', encoding="utf-8"
    )
    try:
        load_required_module_slugs(bad)
    except ValueError as e:
        assert "duplicado" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")
