"""Focused regression tests for security-sensitive request handling."""

from io import BytesIO
from datetime import date
import uuid
import zipfile

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.routers.reports import _query_view_filtered
from app.schemas.bovine import BovineCreate
from app.services import bovine_service
from app.services.document_service import (
    detect_mime_type,
    sanitize_original_filename,
    validate_file_extension,
)
from app.utils.security import create_access_token, decode_token


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
    with pytest.raises(HTTPException) as exc_info:
        _query_view_filtered(None, None, "v_farm_summary; DROP TABLE farm")
    assert exc_info.value.status_code == 400


def test_bovine_and_audit_are_rolled_back_together(monkeypatch) -> None:
    session = _FakeSession()

    def fail_audit(*_args, **_kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(bovine_service, "add_audit_log", fail_audit)
    bovine_data = BovineCreate(
        identification_number="BT-001",
        sex="hembra",
        birth_date=date(2025, 1, 1),
        entry_type="compra",
        entry_date=date(2025, 1, 2),
    )

    with pytest.raises(RuntimeError, match="audit unavailable"):
        bovine_service.create_bovine(
            session, uuid.uuid4(), bovine_data, uuid.uuid4()
        )

    assert session.commits == 0
    assert session.rollbacks == 1


def test_file_signature_overrides_client_mime_type() -> None:
    assert detect_mime_type(b"%PDF-1.7\n", "text/plain") == "application/pdf"


def test_executable_content_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        detect_mime_type(b"MZ\x00\x00not a supported document", "application/pdf")
    assert exc_info.value.status_code == 400


def test_docx_is_identified_from_package_contents() -> None:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>")

    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert detect_mime_type(buffer.getvalue(), "application/zip") == mime


def test_misleading_extension_is_rejected() -> None:
    with pytest.raises(HTTPException):
        validate_file_extension("malware.exe", "application/pdf")


def test_original_filename_cannot_escape_storage_or_inject_headers() -> None:
    assert sanitize_original_filename("..\\..\\malicious\r\n.pdf") == "malicious.pdf"
