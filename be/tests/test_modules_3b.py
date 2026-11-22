"""
Pruebas de la Parte 3b del refactor: módulos documents, reports y notifications.

¿Qué? Cada servicio se prueba con repositorio y colaboradores falsos (sin BD,
      sin disco, sin correo). El almacenamiento local se prueba sobre un
      directorio temporal real. La frontera HTTP se prueba con TestClient.
¿Para qué? Demostrar que cada módulo cumple el contrato de su README.md:
           mismos códigos de estado, mismos mensajes y mismas garantías.
¿Impacto? Si se rompe el borrado del archivo huérfano, la idempotencia de las
          notificaciones o la validación de fechas de los reportes, falla aquí.
"""

import uuid
from collections.abc import Iterator
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.documents.schemas import DocumentAssociationEnum, DocumentTypeEnum
from app.modules.documents.service import (
    BOVINE_NOT_IN_FARM,
    EMPTY_FILE,
    FARM_MISMATCH,
    DocumentService,
)
from app.modules.documents.storage import LocalDocumentStorage
from app.modules.notifications.models import UserNotificationPref
from app.modules.notifications.service import NOTIFICATION_NOT_FOUND, NotificationService
from app.modules.reports.schemas import ReportCategory, ReportFilterParams
from app.modules.reports.service import (
    END_IN_FUTURE,
    FARM_NOT_FOUND,
    START_AFTER_END,
    START_IN_FUTURE,
    ReportService,
)
from app.shared.exceptions import BusinessRuleError, InvalidRequestError, NotFoundError
from app.shared.ports import BovineRef, LowStockItem, SanitaryDue

FARM = uuid.uuid4()
USER = uuid.uuid4()
COW = uuid.uuid4()
PDF = b"%PDF-1.7\n%contenido de prueba\n"


# ═══════════════════════════════════════════════════════════════
# documents
# ═══════════════════════════════════════════════════════════════


class MemoryStorage:
    """DocumentStorage en memoria: registra qué se guardó y qué se borró."""

    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}
        self.deleted: list[str] = []

    def save(self, content: bytes, extension: str) -> str:
        name = f"{uuid.uuid4()}.{extension}"
        self.files[name] = content
        return name

    def read(self, stored_filename: str) -> bytes:
        if stored_filename not in self.files:
            raise NotFoundError("File not found")
        return self.files[stored_filename]

    def delete(self, stored_filename: str) -> None:
        self.files.pop(stored_filename, None)
        self.deleted.append(stored_filename)


class FakeDocumentRepo:
    def __init__(self, fail_on_commit: bool = False) -> None:
        self.rows: dict[uuid.UUID, Any] = {}
        self.events: list[str] = []
        self.fail_on_commit = fail_on_commit

    def get_active_in_farm(self, farm_id: uuid.UUID, document_id: uuid.UUID) -> Any:
        doc = self.rows.get(document_id)
        return doc if doc is not None and doc.farm_id == farm_id and doc.is_active is not False else None

    def list_active(self, farm_id: uuid.UUID, **_: Any) -> tuple[list[Any], int]:
        docs = [d for d in self.rows.values() if d.farm_id == farm_id and d.is_active is not False]
        return docs, len(docs)

    def add(self, document: Any) -> None:
        document.id = document.id or uuid.uuid4()
        self.rows[document.id] = document
        self.events.append("add")

    def flush(self) -> None:
        self.events.append("flush")

    def commit(self) -> None:
        if self.fail_on_commit:
            raise RuntimeError("BD caída")
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")

    def refresh(self, document: Any) -> None:
        document.uploaded_at = document.uploaded_at or datetime.now()
        document.is_active = True if document.is_active is None else document.is_active
        self.events.append("refresh")


def _docs(fail_on_commit: bool = False) -> tuple[DocumentService, FakeDocumentRepo, MemoryStorage, MagicMock]:
    repo, storage, audit = FakeDocumentRepo(fail_on_commit), MemoryStorage(), MagicMock()

    def find_bovine(farm_id: uuid.UUID, bovine_id: uuid.UUID) -> BovineRef | None:
        return BovineRef(id=bovine_id, sex="hembra") if (farm_id, bovine_id) == (FARM, COW) else None

    return DocumentService(repo, storage, find_bovine, audit), repo, storage, audit  # type: ignore[arg-type]


def _upload(service: DocumentService, **overrides: Any) -> Any:
    values: dict[str, Any] = {
        "file_content": PDF,
        "declared_mime": "application/pdf",
        "filename": "certificado.pdf",
        "document_type": DocumentTypeEnum.PDF,
        "association_type": DocumentAssociationEnum.FARM,
        "associated_entity_id": FARM,
        "description": None,
        "user_id": USER,
    }
    values.update(overrides)
    return service.upload_document(FARM, **values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"file_content": b""}, EMPTY_FILE),
        ({"file_content": b"MZ\x00\x00ejecutable"}, "Formato de archivo no permitido o contenido no reconocido"),
        ({"document_type": DocumentTypeEnum.IMAGE}, "El contenido del archivo no coincide con el tipo permitido"),
        ({"filename": "certificado.exe"}, "La extensión del archivo no coincide con su contenido"),
        ({"associated_entity_id": uuid.uuid4()}, FARM_MISMATCH),
        ({"association_type": DocumentAssociationEnum.BOVINE, "associated_entity_id": uuid.uuid4()}, BOVINE_NOT_IN_FARM),
    ],
)
def test_documents_upload_rejects_and_stores_nothing(overrides: dict[str, Any], message: str) -> None:
    service, repo, storage, _ = _docs()

    with pytest.raises(BusinessRuleError) as exc:
        _upload(service, **overrides)
    assert exc.value.message == message
    assert storage.files == {} and repo.rows == {}


def test_documents_upload_saves_file_then_metadata_and_audit() -> None:
    service, repo, storage, audit = _docs()

    doc = _upload(service, association_type=DocumentAssociationEnum.BOVINE, associated_entity_id=COW, filename="..\\..\\vacuna.pdf")

    assert doc.original_filename == "vacuna.pdf"  # nombre saneado
    assert doc.stored_filename in storage.files and doc.stored_filename.endswith(".pdf")
    assert doc.mime_type == "application/pdf" and doc.file_size == len(PDF)
    assert repo.events == ["add", "flush", "commit", "refresh"]
    assert audit.call_args.kwargs["details"]["associated_to"] == f"bovine:{COW}"


def test_documents_db_failure_removes_orphan_file() -> None:
    service, repo, storage, _ = _docs(fail_on_commit=True)

    with pytest.raises(RuntimeError):
        _upload(service)
    assert "rollback" in repo.events
    assert storage.files == {} and len(storage.deleted) == 1


def test_documents_delete_is_logical_and_removes_file() -> None:
    service, repo, storage, audit = _docs()
    doc = _upload(service)
    stored = doc.stored_filename

    service.delete_document(FARM, doc.id, USER)

    assert doc.is_active is False and doc.deleted_by == USER and doc.deleted_at is not None
    assert stored in storage.deleted
    assert doc.id in repo.rows  # el registro se conserva para la auditoría
    assert audit.call_args.kwargs["action"] == "delete"
    with pytest.raises(NotFoundError):
        service.get_document(FARM, doc.id)


def test_documents_download_returns_bytes_name_and_mime() -> None:
    service, _, _, _ = _docs()
    doc = _upload(service, filename="informe.pdf")

    assert service.get_document_for_download(FARM, doc.id) == (PDF, "informe.pdf", "application/pdf")


def test_local_storage_roundtrip(tmp_path: Path) -> None:
    storage = LocalDocumentStorage(tmp_path / "docs")

    name = storage.save(b"hola", "txt")
    assert storage.read(name) == b"hola"
    assert "/" not in name and name.endswith(".txt")

    storage.delete(name)
    with pytest.raises(NotFoundError) as exc:
        storage.read(name)
    assert exc.value.message == "File not found"
    storage.delete(name)  # borrar dos veces no falla


# ═══════════════════════════════════════════════════════════════
# reports
# ═══════════════════════════════════════════════════════════════


def _reports(**repo_values: Any) -> tuple[ReportService, MagicMock]:
    repo = MagicMock()
    repo.farm_name.return_value = "La Esperanza"
    repo.farm_statistics.return_value = {"total_bovines": 10, "males": 4, "females": 6, "avg_weight": 420.5}
    repo.total_milk_liters.return_value = Decimal("300")
    repo.milking_days.return_value = 3
    repo.calves_by_age_group.return_value = {"0-3 meses": 2, "6-12 meses": 1}
    repo.treatments_by_type.return_value = {"vacuna": 4, "desparasitacion": 1}
    repo.active_sanitary_plans.return_value = 2
    repo.pending_treatments.return_value = 3
    repo.economic_rows.return_value = [(Decimal("500"), 0, "venta_leche"), (0, Decimal("120"), "compra_insumo")]
    repo.accessible_farm_ids.return_value = [str(FARM)]
    for key, value in repo_values.items():
        getattr(repo, key).return_value = value
    return ReportService(repo, today=lambda: date(2026, 11, 20)), repo


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (date(2026, 11, 10), date(2026, 11, 1), START_AFTER_END),
        (date(2026, 12, 1), None, START_IN_FUTURE),
        (None, date(2026, 12, 1), END_IN_FUTURE),
    ],
)
def test_reports_reject_invalid_date_ranges_before_querying(start: date | None, end: date | None, message: str) -> None:
    service, repo = _reports()

    with pytest.raises(InvalidRequestError) as exc:
        service.generate_report(FARM, ReportFilterParams(start_date=start, end_date=end))
    assert exc.value.message == message
    repo.farm_name.assert_not_called()


def test_reports_unknown_farm_is_404() -> None:
    service, _ = _reports(farm_name=None)

    with pytest.raises(NotFoundError) as exc:
        service.generate_report(FARM, ReportFilterParams())
    assert exc.value.message == FARM_NOT_FOUND


def test_reports_full_report_aggregates_all_categories() -> None:
    service, _ = _reports()

    report = service.generate_report(FARM, ReportFilterParams())

    assert report.farm_name == "La Esperanza"
    assert report.productive is not None and report.productive.total_calves == 3
    assert report.productive.avg_milk_per_day == 100.0  # 300 L / 3 días con ordeño
    assert report.sanitary is not None and report.sanitary.total_treatments == 5
    assert report.sanitary.pending_treatments == 3
    assert report.economic is not None and report.economic.balance == 380.0
    assert report.economic.income_by_activity == {"venta_leche": 500.0}


def test_reports_single_category_and_range_days() -> None:
    service, repo = _reports()

    report = service.generate_report(
        FARM,
        ReportFilterParams(category=ReportCategory.PRODUCTIVE, start_date=date(2026, 11, 1), end_date=date(2026, 11, 10)),
    )

    assert report.sanitary is None and report.economic is None
    assert report.productive is not None and report.productive.avg_milk_per_day == 30.0  # 300 L / 10 días
    repo.milking_days.assert_not_called()


def test_reports_global_views_are_empty_without_farms() -> None:
    service, repo = _reports(accessible_farm_ids=[])

    assert service.view_for_user(USER, "v_pending_tasks") == []
    repo.view_rows.assert_not_called()


def test_reports_statistics_without_data_returns_message() -> None:
    service, _ = _reports(farm_statistics=None)

    assert service.farm_statistics(FARM) == {"message": "Farm without statistics"}


# ═══════════════════════════════════════════════════════════════
# notifications
# ═══════════════════════════════════════════════════════════════

NOW = datetime(2026, 11, 20, 8, 0)
OVERDUE_PLAN = SanitaryDue(uuid.uuid4(), "Aftosa", "vacuna", date(2026, 11, 1), COW, None)
UPCOMING_PLAN = SanitaryDue(uuid.uuid4(), "Ivermectina", "desparasitacion", date(2026, 11, 22), None, uuid.uuid4())
LOW_ITEM = LowStockItem(uuid.uuid4(), "Sal mineral", "suplemento", Decimal("2"), Decimal("10"), "kg")


class FakeSanitary:
    def overdue(self, farm_id: uuid.UUID, now: datetime) -> list[SanitaryDue]:
        return [OVERDUE_PLAN]

    def upcoming(self, farm_id: uuid.UUID, now: datetime, until: datetime) -> list[SanitaryDue]:
        assert until == now + timedelta(days=7)
        return [UPCOMING_PLAN]


def _notifications(channel: str = "email", already_sent: bool = False, **flags: bool) -> tuple[NotificationService, MagicMock, list[dict[str, Any]]]:
    repo = MagicMock()
    repo.get_prefs.return_value = UserNotificationPref(
        user_id=USER, farm_id=FARM, channel=channel,
        notify_sanitary=flags.get("sanitary", True), notify_low_stock=flags.get("low_stock", True),
        notify_reproductive=True, notify_birth=True, frequency="real_time",
    )
    repo.exists_since.return_value = already_sent
    sent: list[dict[str, Any]] = []

    async def send_email(**kwargs: Any) -> None:
        sent.append(kwargs)

    service = NotificationService(
        repo,
        sanitary_alerts=FakeSanitary(),
        low_stock=lambda farm_id: [LOW_ITEM],
        farm_members=lambda farm_id: [USER],
        user_email=lambda user_id: "ganadero@example.com",
        send_email=send_email,
        now=lambda: NOW,
    )
    return service, repo, sent


def test_notifications_active_alerts_shape() -> None:
    service, _, _ = _notifications()

    alerts = service.active_alerts(FARM)

    assert alerts["overdue"][0] == {
        "id": str(OVERDUE_PLAN.id), "vaccine_or_treatment_name": "Aftosa", "treatment_type": "vacuna",
        "next_scheduled_date": "2026-11-01", "bovine_id": str(COW), "land_plot_id": None,
    }
    assert alerts["upcoming"][0]["land_plot_id"] == str(UPCOMING_PLAN.land_plot_id)
    assert alerts["low_stock"][0] == {
        "id": str(LOW_ITEM.id), "name": "Sal mineral", "category": "suplemento",
        "current_stock": 2.0, "min_stock_alert": 10.0, "unit_of_measure": "kg",
    }


def test_notifications_cycle_logs_and_emails_each_candidate() -> None:
    import asyncio

    service, repo, sent = _notifications(channel="email")

    created = asyncio.run(service.run_notification_cycle(FARM))

    assert created == 3  # vencido + próximo + stock bajo
    assert [c.args[0].type for c in repo.add.call_args_list] == ["sanitary", "sanitary", "low_stock"]
    assert all(c.args[0].channel == "email" for c in repo.add.call_args_list)
    assert len(sent) == 3 and sent[0]["to_email"] == "ganadero@example.com"
    assert sent[0]["subject"] == "BoviTrack — Plan sanitario vencido: Aftosa"
    repo.commit.assert_called_once()
    # Ventana de deduplicación: 24 h antes de "ahora".
    assert repo.exists_since.call_args.args[3] == NOW - timedelta(hours=24)


def test_notifications_cycle_is_idempotent() -> None:
    import asyncio

    service, repo, sent = _notifications(already_sent=True)

    assert asyncio.run(service.run_notification_cycle(FARM)) == 0
    repo.add.assert_not_called()
    assert sent == []


def test_notifications_cycle_respects_preferences_and_channel() -> None:
    import asyncio

    service, repo, sent = _notifications(channel="in_app", sanitary=False)

    assert asyncio.run(service.run_notification_cycle(FARM)) == 1  # solo stock bajo
    assert repo.add.call_args.args[0].channel == "in_app"
    assert sent == []  # in_app no envía correo


def test_notifications_mark_as_read_of_someone_else_is_404() -> None:
    service, repo, _ = _notifications()
    repo.get_log_for_user.return_value = None

    with pytest.raises(NotFoundError) as exc:
        service.mark_as_read(USER, FARM, uuid.uuid4())
    assert exc.value.message == NOTIFICATION_NOT_FOUND


def test_notifications_prefs_are_created_with_defaults() -> None:
    service, repo, _ = _notifications()
    repo.get_prefs.return_value = None

    pref = service.get_or_create_prefs(USER, FARM)

    assert (pref.channel, pref.frequency, pref.notify_sanitary, pref.notify_birth) == ("email", "real_time", True, True)
    repo.add.assert_called_once_with(pref)
    repo.commit.assert_called_once()


# ═══════════════════════════════════════════════════════════════
# Frontera HTTP de los tres módulos
# ═══════════════════════════════════════════════════════════════


class _AllowAllSession:
    def execute(self, stmt: Any) -> SimpleNamespace:
        entity = stmt.column_descriptions[0]["entity"].__name__
        value: Any = (
            SimpleNamespace(role_id=uuid.uuid4())
            if entity == "UserFarm"
            else SimpleNamespace(can_create=True, can_read=True, can_update=True, can_delete=True)
        )
        return SimpleNamespace(scalar_one_or_none=lambda: value)

    def get(self, model: Any, key: Any) -> SimpleNamespace:
        return SimpleNamespace(is_active=True)


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.core.database import get_db
    from app.core.limiter import limiter
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.documents.dependencies import get_document_service
    from app.modules.notifications.dependencies import get_notification_service
    from app.modules.reports.dependencies import get_report_service

    docs, _, _, _ = _docs()
    notifications, notif_repo, _ = _notifications()
    notif_repo.get_log_for_user.return_value = None
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    app.dependency_overrides[get_document_service] = lambda: docs
    app.dependency_overrides[get_notification_service] = lambda: notifications
    app.dependency_overrides[get_report_service] = lambda: _reports()[0]
    was_enabled, limiter.enabled = limiter.enabled, False
    try:
        yield TestClient(app)
    finally:
        limiter.enabled = was_enabled
        app.dependency_overrides.clear()


def test_http_document_upload_and_download(client: TestClient) -> None:
    base = f"/api/v1/farms/{FARM}/documents"
    form = {"document_type": "pdf", "association_type": "farm", "associated_entity_id": str(FARM)}

    created = client.post(base, data=form, files={"file": ("acta.pdf", PDF, "application/pdf")})
    assert created.status_code == 201, created.text
    doc_id = created.json()["id"]

    download = client.get(f"{base}/{doc_id}/download")
    assert download.status_code == 200 and download.content == PDF
    assert download.headers["content-disposition"].startswith('attachment; filename="acta.pdf"')

    empty = client.post(base, data=form, files={"file": ("vacio.pdf", b"", "application/pdf")})
    assert (empty.status_code, empty.json()) == (400, {"detail": EMPTY_FILE})

    missing = client.get(f"{base}/{uuid.uuid4()}/download")
    assert (missing.status_code, missing.json()) == (404, {"detail": "Document not found"})


def test_http_reports_validation_is_422(client: TestClient) -> None:
    response = client.get(f"/api/v1/farms/{FARM}/reports", params={"start_date": "2026-11-10", "end_date": "2026-11-01"})

    assert (response.status_code, response.json()) == (422, {"detail": START_AFTER_END})


def test_http_reports_excel_export(client: TestClient) -> None:
    response = client.get(f"/api/v1/farms/{FARM}/reports", params={"export": "excel"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert response.content[:2] == b"PK"  # un .xlsx es un ZIP


def test_http_alerts_preferences_and_read(client: TestClient) -> None:
    base = f"/api/v1/farms/{FARM}/alerts"

    bad = client.put(f"{base}/preferences", json={"channel": "paloma_mensajera"})
    assert bad.status_code == 422 and bad.json()["detail"].startswith("Canal inválido: paloma_mensajera")

    read = client.put(f"{base}/history/{uuid.uuid4()}/read")
    assert (read.status_code, read.json()) == (404, {"detail": NOTIFICATION_NOT_FOUND})

    alerts = client.get(base)
    assert alerts.status_code == 200 and set(alerts.json()) == {"overdue", "upcoming", "low_stock"}


@pytest.mark.parametrize("entrypoint", ["app.modules.documents", "app.modules.reports", "app.modules.notifications"])
def test_module_boots_like_uvicorn(entrypoint: str) -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", f"import {entrypoint}; import app.main"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr[-1500:]
