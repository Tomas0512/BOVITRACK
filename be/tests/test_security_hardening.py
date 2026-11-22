"""Focused regression tests for security-sensitive request handling."""

from io import BytesIO
from datetime import date
import uuid
import zipfile

import pytest

from app.core.config import Settings
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportService
from app.modules.livestock.repository import BovineRepository
from app.modules.livestock.schemas import BovineCreate
from app.modules.livestock.service import BovineService
from app.modules.documents.file_rules import (
    detect_mime_type,
    sanitize_original_filename,
    validate_file_extension,
)
from app.core.security import create_access_token, decode_token
from app.shared.exceptions import BusinessRuleError


class _EmptyQueryResult:
    def scalar_one_or_none(self):
        return None


class _FakeSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def execute(self, _statement):
        return _EmptyQueryResult()

    def add(self, _record) -> None:
        pass

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def refresh(self, _record) -> None:
        pass


def test_settings_reject_short_jwt_secret() -> None:
    with pytest.raises(ValueError):
        Settings(DATABASE_URL="postgresql://localhost/test", SECRET_KEY="too-short")


def test_jwt_secret_accepts_at_least_32_characters() -> None:
    settings = Settings(
        DATABASE_URL="postgresql://localhost/test",
        SECRET_KEY="a" * 32,
    )
    assert len(settings.SECRET_KEY) == 32


def test_created_access_tokens_include_issued_at() -> None:
    payload = decode_token(create_access_token({"sub": "test-user"}))
    assert payload is not None
    assert payload["type"] == "access"
    assert "iat" in payload


def test_report_view_must_be_allowlisted_before_database_access() -> None:
    # Sesión None: si el servicio intentara consultar la BD antes de validar,
    # fallaría con AttributeError en vez de BusinessRuleError (-> 400).
    service = ReportService(ReportRepository(None))  # type: ignore[arg-type]
    with pytest.raises(BusinessRuleError) as exc_info:
        service.view_for_user(None, "v_farm_summary; DROP TABLE farm")  # type: ignore[arg-type]
    assert exc_info.value.message == "Vista de reporte no permitida"


def test_bovine_and_audit_are_rolled_back_together() -> None:
    session = _FakeSession()

    def fail_audit(*_args, **_kwargs):
        raise RuntimeError("audit unavailable")

    # Refactor (Parte 3d): la auditoría se inyecta al servicio en vez de parchearse.
    unused = lambda *_a, **_k: None  # noqa: E731 — puertos que este caso no usa
    service = BovineService(BovineRepository(session), unused, unused, unused, unused, unused, fail_audit)
    bovine_data = BovineCreate(
        identification_number="BT-001",
        sex="hembra",
        birth_date=date(2025, 1, 1),
        entry_type="compra",
        entry_date=date(2025, 1, 2),
    )

    with pytest.raises(RuntimeError, match="audit unavailable"):
        service.create_bovine(uuid.uuid4(), bovine_data, uuid.uuid4())

    assert session.commits == 0
    assert session.rollbacks == 1


def test_file_signature_overrides_client_mime_type() -> None:
    assert detect_mime_type(b"%PDF-1.7\n", "text/plain") == "application/pdf"


def test_executable_content_is_rejected() -> None:
    # Las reglas de contenido lanzan un error de dominio; app.core.error_handlers
    # lo responde con 400 (ver test_core_shared.py).
    with pytest.raises(BusinessRuleError) as exc_info:
        detect_mime_type(b"MZ\x00\x00not a supported document", "application/pdf")
    assert exc_info.value.message == "Formato de archivo no permitido o contenido no reconocido"


def test_docx_is_identified_from_package_contents() -> None:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>")

    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert detect_mime_type(buffer.getvalue(), "application/zip") == mime


def test_misleading_extension_is_rejected() -> None:
    with pytest.raises(BusinessRuleError):
        validate_file_extension("malware.exe", "application/pdf")


def test_original_filename_cannot_escape_storage_or_inject_headers() -> None:
    assert sanitize_original_filename("..\\..\\malicious\r\n.pdf") == "malicious.pdf"
