"""
Pruebas de la Parte 6b-1 (seguridad):
  - Bloqueo de login en la tabla login_attempt: compartido entre procesos, sobrevive
    a reinicios, ventana de 15 minutos, no guarda el correo y se limpia solo.
  - Eventos de seguridad (core/security_events): AuthService los registra con el
    motivo y la IP, y nunca escribe el correo completo ni la contraseña.
  - La ruta de login usa de verdad la tabla (de punta a punta por HTTP).
"""

import hashlib
import json
import logging
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todas las tablas
from app.core import security_events
from app.core.security import hash_password
from app.modules.identity.models import LoginAttempt, PasswordResetToken, User
from app.modules.identity.repository import LoginAttemptRepository, UserRepository
from app.modules.identity.schemas import ResetPasswordRequest, UserLogin
from app.modules.identity.service import AuthService, LoginThrottle
from app.shared.exceptions import AuthenticationError, PermissionDeniedError, TooManyAttemptsError

PASSWORD = "Clave#2026"
T0 = datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def db() -> Iterator[Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for name in ("users", "login_attempt", "password_reset_tokens", "audit_log"):
        Base.metadata.tables[name].create(engine)
    with Session(engine) as session:
        for email, active in (("ana@x.com", True), ("rosa@x.com", False)):
            session.add(User(id=uuid.uuid4(), first_name="Ana", last_name="Ruiz", document_type="CC",
                             document_number=email, email=email, phone="300", hashed_password=hash_password(PASSWORD),
                             is_active=active, token_version=0, created_at=T0, updated_at=T0))
        session.commit()
        yield session


def _throttle(db: Any, clock: list[datetime]) -> LoginThrottle:
    """Un LoginThrottle como el de cada request: la cuenta vive en la tabla, no en él."""
    return LoginThrottle(5, 15, clock=lambda: clock[0], store=LoginAttemptRepository(db))


def _auth(db: Any, clock: list[datetime]) -> AuthService:
    async def no_email(_email: str, _token: str) -> None:
        return None

    return AuthService(UserRepository(db), throttle=_throttle(db, clock), record_audit=lambda **kw: None,
                       send_password_reset=no_email, send_email_verification=no_email, security_log=security_events)


# ═══════════════════════════════════════════════════════════════
# Bloqueo de login persistente
# ═══════════════════════════════════════════════════════════════


def test_lockout_is_shared_between_processes_and_survives_a_restart(db: Any) -> None:
    clock = [T0]
    worker_a, worker_b = _throttle(db, clock), _throttle(db, clock)  # dos procesos de la API
    for worker in (worker_a, worker_a, worker_b, worker_b):
        assert worker.register_failure("Ana@x.com") is False
    assert worker_a.register_failure("ana@x.com") is True  # 5.º fallo, sumando los dos procesos

    restarted = _throttle(db, clock)  # la API se reinicia: el bloqueo sigue
    with pytest.raises(TooManyAttemptsError) as exc:
        restarted.ensure_not_locked("ana@x.com")
    assert exc.value.message == "Demasiados intentos fallidos. Intente de nuevo en 16 minuto(s)."

    clock[0] += timedelta(minutes=15, seconds=1)
    restarted.ensure_not_locked("ana@x.com")  # pasó el bloqueo


def test_failures_outside_the_window_start_over_and_success_clears(db: Any) -> None:
    clock = [T0]
    throttle = _throttle(db, clock)
    for _ in range(4):
        throttle.register_failure("ana@x.com")
    clock[0] += timedelta(minutes=16)  # 4 fallos viejos ya no cuentan
    assert throttle.register_failure("ana@x.com") is False
    assert db.get(LoginAttempt, LoginThrottle.key("ana@x.com")).failed_count == 1

    throttle.reset("ana@x.com")  # login correcto
    assert db.query(LoginAttempt).count() == 0


def test_the_email_is_never_stored_and_stale_rows_are_purged(db: Any) -> None:
    clock = [T0]
    throttle = _throttle(db, clock)
    throttle.register_failure("ana@x.com")
    [row] = db.query(LoginAttempt).all()
    assert row.email_hash == hashlib.sha256(b"ana@x.com").hexdigest() and "ana" not in repr(row)

    clock[0] += timedelta(days=2)  # el siguiente fallo de cualquiera limpia las filas viejas
    throttle.register_failure("otra@x.com")
    assert [r.email_hash for r in db.query(LoginAttempt)] == [LoginThrottle.key("otra@x.com")]


# ═══════════════════════════════════════════════════════════════
# Eventos de seguridad
# ═══════════════════════════════════════════════════════════════


def _events(caplog: pytest.LogCaptureFixture) -> list[dict[str, Any]]:
    return [json.loads(r.getMessage()) for r in caplog.records if r.name == "security.audit"]


def test_login_flow_writes_security_events_without_personal_data(db: Any, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="security.audit")
    clock = [T0]
    service = _auth(db, clock)
    wrong = UserLogin(email="ana@x.com", password="mala-clave")

    for _ in range(5):
        with pytest.raises(AuthenticationError):
            service.login(wrong, ip="10.0.0.7")
    with pytest.raises(TooManyAttemptsError):
        service.login(UserLogin(email="ana@x.com", password=PASSWORD), ip="10.0.0.7")
    clock[0] += timedelta(minutes=16)
    service.login(UserLogin(email="ana@x.com", password=PASSWORD), ip="10.0.0.8")
    with pytest.raises(PermissionDeniedError):
        service.login(UserLogin(email="rosa@x.com", password=PASSWORD), ip="10.0.0.9")

    events = [(e["event"], e.get("reason"), e["ip"]) for e in _events(caplog)]
    assert events == [("login_failed", "invalid_credentials", "10.0.0.7")] * 5 + [
        ("login_locked", None, "10.0.0.7"),
        ("login_failed", "locked", "10.0.0.7"),
        ("login_success", None, "10.0.0.8"),
        ("login_failed", "account_disabled", "10.0.0.9"),
    ]
    logged = caplog.text
    assert "a***@x.com" in logged and "ana@x.com" not in logged and "mala-clave" not in logged and PASSWORD not in logged


def test_password_reset_writes_security_events(db: Any, caplog: pytest.LogCaptureFixture) -> None:
    import asyncio

    caplog.set_level(logging.INFO, logger="security.audit")
    service = _auth(db, [T0])
    asyncio.run(service.request_password_reset("nadie@x.com", ip="10.0.0.1"))  # existe o no: mismo evento
    asyncio.run(service.request_password_reset("ana@x.com", ip="10.0.0.1"))
    row = db.query(PasswordResetToken).one()
    row.expires_at = row.expires_at.replace(tzinfo=timezone.utc)  # SQLite la devuelve sin zona; Postgres no
    token = row.token
    service.reset_password(ResetPasswordRequest(token=token, new_password="Nueva#2026", confirm_password="Nueva#2026"),
                           ip="10.0.0.2")

    user = db.query(User).filter_by(email="ana@x.com").one()
    assert [(e["event"], e["ip"], e.get("user_id")) for e in _events(caplog)] == [
        ("password_reset_requested", "10.0.0.1", None),
        ("password_reset_requested", "10.0.0.1", None),
        ("password_changed", "10.0.0.2", str(user.id)),
    ]


def test_security_events_reach_the_server_logs() -> None:
    """Uvicorn no configura el logger raíz: el logger trae su propio handler."""
    import subprocess
    import sys

    code = "from app.core import security_events as s; s.log_login_failed('ana@x.com', 'invalid_credentials', '1.2.3.4')"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    line = result.stderr.strip()
    assert line.startswith("SECURITY ") and json.loads(line.removeprefix("SECURITY "))["email"] == "a***@x.com"


# ═══════════════════════════════════════════════════════════════
# De punta a punta por HTTP
# ═══════════════════════════════════════════════════════════════


def test_login_route_locks_through_the_table(db: Any) -> None:
    from app.core.database import get_db
    from app.core.limiter import limiter
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db
    was_enabled, limiter.enabled = limiter.enabled, False
    try:
        http = TestClient(app)
        for _ in range(5):
            assert http.post("/api/v1/auth/login", json={"email": "ana@x.com", "password": "mala"}).status_code == 401
        locked = http.post("/api/v1/auth/login", json={"email": "ana@x.com", "password": PASSWORD})
        assert locked.status_code == 429 and "Demasiados intentos" in locked.json()["detail"]
        row = db.get(LoginAttempt, LoginThrottle.key("ana@x.com"))
        assert row.locked_until is not None and row.failed_count == 0
    finally:
        app.dependency_overrides.clear()
        limiter.enabled = was_enabled

