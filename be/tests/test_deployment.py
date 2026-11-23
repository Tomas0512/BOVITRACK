"""
Pruebas de la Parte 5 del refactor: listo para desplegar.

  - Configuración: en producción la API no arranca con ajustes inseguros.
  - entrypoint.sh: migraciones antes de arrancar (y se detiene si fallan),
    uvicorn sin --reload en producción y con la IP real del cliente.
  - Imagen: los documentos subidos y las pruebas no entran en la imagen.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings

BE = Path(__file__).resolve().parents[1]
BASE = {"DATABASE_URL": "postgresql://u:p@db/x", "SECRET_KEY": "s" * 32, "ENVIRONMENT": "production"}


def _settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **{**BASE, **overrides})  # type: ignore[arg-type]


# ═══════════════════════════════════════════════════════════════
# Configuración de producción
# ═══════════════════════════════════════════════════════════════


def test_production_accepts_a_safe_configuration() -> None:
    assert _settings(EMAIL_BACKEND="smtp", SMTP_HOST="smtp.gmail.com").ENVIRONMENT == "production"
    assert _settings(EMAIL_BACKEND="resend", RESEND_API_KEY="re_123").EMAIL_BACKEND == "resend"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"EMAIL_BACKEND": "log"}, "no entrega correos reales"),
        ({"EMAIL_BACKEND": "mailpit"}, "no entrega correos reales"),
        ({"EMAIL_BACKEND": "smtp", "SMTP_HOST": ""}, "necesita SMTP_HOST"),
        ({"EMAIL_BACKEND": "resend"}, "necesita RESEND_API_KEY"),
        ({"EMAIL_BACKEND": "smtp", "SMTP_HOST": "h", "RATE_LIMIT_ENABLED": False}, "RATE_LIMIT_ENABLED debe ser true"),
    ],
)
def test_production_refuses_unsafe_settings(overrides: dict, message: str) -> None:
    with pytest.raises(ValidationError) as exc:
        _settings(**overrides)
    assert message in str(exc.value)


def test_development_keeps_its_conveniences_and_environment_is_validated() -> None:
    dev = _settings(ENVIRONMENT="development", EMAIL_BACKEND="log", RATE_LIMIT_ENABLED=False)
    assert (dev.EMAIL_BACKEND, dev.RATE_LIMIT_ENABLED) == ("log", False)
    with pytest.raises(ValidationError):
        _settings(ENVIRONMENT="prod")  # un error de tipeo no puede desactivar las protecciones


# ═══════════════════════════════════════════════════════════════
# entrypoint.sh (se ejecuta con "alembic" y "uvicorn" falsos)
# ═══════════════════════════════════════════════════════════════


def _run_entrypoint(tmp_path: Path, env: dict[str, str], alembic_exit: int = 0) -> tuple[int, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    for name, code in (("alembic", alembic_exit), ("uvicorn", 0)):
        fake = bin_dir / name
        fake.write_text(f'#!/bin/sh\necho "{name} $*" >> "{log}"\nexit {code}\n')
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    result = subprocess.run(
        ["sh", str(BE / "entrypoint.sh")],
        env={"PATH": f"{bin_dir}:{os.environ['PATH']}", **env},
        capture_output=True, text=True, check=False,
    )
    return result.returncode, log.read_text() if log.exists() else ""


@pytest.mark.skipif(shutil.which("sh") is None, reason="necesita un shell POSIX")
def test_entrypoint_production_runs_without_reload_and_with_proxy_headers(tmp_path: Path) -> None:
    code, calls = _run_entrypoint(tmp_path, {"ENVIRONMENT": "production", "WEB_CONCURRENCY": "2"})

    alembic, uvicorn = calls.strip().splitlines()
    assert code == 0 and alembic == "alembic upgrade head"
    assert "--reload" not in uvicorn
    assert "--workers 2" in uvicorn and "--proxy-headers" in uvicorn and "--forwarded-allow-ips=*" in uvicorn


@pytest.mark.skipif(shutil.which("sh") is None, reason="necesita un shell POSIX")
def test_entrypoint_development_reloads(tmp_path: Path) -> None:
    _, calls = _run_entrypoint(tmp_path, {})

    assert "--reload" in calls.strip().splitlines()[-1]


@pytest.mark.skipif(shutil.which("sh") is None, reason="necesita un shell POSIX")
def test_entrypoint_stops_if_migrations_fail(tmp_path: Path) -> None:
    code, calls = _run_entrypoint(tmp_path, {"ENVIRONMENT": "production"}, alembic_exit=1)

    assert code != 0
    assert "uvicorn" not in calls  # nunca arranca la API con un esquema viejo


# ═══════════════════════════════════════════════════════════════
# Contenido de la imagen
# ═══════════════════════════════════════════════════════════════


def test_dockerignore_keeps_uploads_and_tests_out_of_the_image() -> None:
    dockerignore_file = BE / ".dockerignore"
    if not dockerignore_file.exists():
        pytest.skip(".dockerignore no se copia a la imagen (se prueba desde el repo)")
    ignored = {line.strip() for line in dockerignore_file.read_text().splitlines()}
    assert {"storage/", "tests/", ".env"} <= ignored


def test_production_hides_docs_and_the_openapi_schema() -> None:
    """En producción no se publican /docs, /redoc ni /openapi.json (que describe toda la API)."""
    code = (
        "from fastapi.testclient import TestClient; from app.main import app; c = TestClient(app); "
        "print([c.get(p).status_code for p in ('/docs', '/redoc', '/openapi.json')])"
    )
    env = {**os.environ, "ENVIRONMENT": "production", "EMAIL_BACKEND": "smtp", "SMTP_HOST": "smtp.example.com",
           "RATE_LIMIT_ENABLED": "true"}
    result = subprocess.run(["python", "-c", code], env=env, capture_output=True, text=True, check=False, cwd=BE)
    assert result.returncode == 0, result.stderr[-800:]
    assert result.stdout.strip() == "[404, 404, 404]"


def test_production_never_writes_email_links_to_the_logs(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Si el correo falla, en producción NO se escribe el enlace (lleva un token válido)."""
    from app.core import email

    link = "https://bovitrack.example/reset-password?token=SECRETO-123"
    monkeypatch.setattr(email.settings, "ENVIRONMENT", "production")
    with caplog.at_level("INFO"):
        email._log_fallback("RECUPERACIÓN", "ana@x.com", link)
    assert "SECRETO-123" not in caplog.text and "NO enviado" in caplog.text

    caplog.clear()
    monkeypatch.setattr(email.settings, "ENVIRONMENT", "development")
    with caplog.at_level("INFO"):
        email._log_fallback("RECUPERACIÓN", "ana@x.com", link)
    assert "SECRETO-123" in caplog.text  # en desarrollo sigue siendo útil para probar
