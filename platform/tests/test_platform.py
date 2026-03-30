from pathlib import Path

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
    assert r.json().get("database") == "ok"


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
            "password": "longpassword1",
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
        json={"email": "a@b.c", "password": "longpassword1", "full_name": "A"},
    )
    assert r.status_code == 201
    r2 = client.post(
        "/admin/students",
        headers={"Authorization": f"Bearer {tok}"},
        json={"email": "a@b.c", "password": "otherpass12", "full_name": "B"},
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
