"""
Pruebas de la Parte 3e del refactor (dominios base).

3e-1 · audit
  - core.audit_trail.add_audit_log: escribe en la transacción en curso, sin commit.
  - módulo audit: modelo de lectura (cruza users/farm/user_farm SIN importar
    los modelos de identity ni de farms), aislamiento por finca, exportación y
    el guard de acceso a la auditoría del sistema.
"""

import json
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todas las tablas (users, farm, user_farm...)
from app.core.audit_trail import AuditLog, add_audit_log
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditExportFormat, AuditLogFilters
from app.modules.audit.service import JSON_EXPORT_NOT_ALLOWED, AuditService
from app.shared.exceptions import BusinessRuleError

USER = uuid.uuid4()
FARM = uuid.uuid4()
OTHER_FARM = uuid.uuid4()


# ═══════════════════════════════════════════════════════════════
# core.audit_trail
# ═══════════════════════════════════════════════════════════════


def test_add_audit_log_joins_the_current_transaction_without_commit() -> None:
    db = MagicMock()

    add_audit_log(db, user_id=str(USER), farm_id=str(FARM), action="create", entity="bovine",
                  entity_id="b-1", details={"tag": "BT-1", "nota": "ñandú"})

    row = db.add.call_args.args[0]
    assert isinstance(row, AuditLog)
    assert (row.action, row.entity, row.entity_id) == ("create", "bovine", "b-1")
    assert json.loads(row.details) == {"tag": "BT-1", "nota": "ñandú"} and "ñandú" in row.details  # sin escapar
    db.commit.assert_not_called()


# ═══════════════════════════════════════════════════════════════
# Repositorio de lectura contra tablas reales (SQLite)
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def audit_db() -> Iterator[Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.core.database import Base

    engine = create_engine("sqlite://")
    for name in ("users", "role", "farm", "user_farm", "audit_log"):
        Base.metadata.tables[name].create(engine)
    users, farm, user_farm = (Base.metadata.tables[n] for n in ("users", "farm", "user_farm"))
    now = datetime(2026, 11, 20, tzinfo=timezone.utc)
    with Session(engine) as db:
        db.execute(users.insert(), [{"id": USER, "first_name": "Ana", "last_name": "Ruiz", "document_type": "CC",
                                     "document_number": "1", "email": "ana@x.com", "phone": "300",
                                     "hashed_password": "h", "is_active": True, "created_at": now, "updated_at": now}])
        for fid, name in ((FARM, "La Esperanza"), (OTHER_FARM, "Ajena")):
            db.execute(farm.insert(), [{"id": fid, "name": name, "owner_id": USER, "is_active": True,
                                        "address": "Vereda 1", "department_id": uuid.uuid4(),
                                        "city_municipality": "Montería", "total_area": 10, "purpose_id": uuid.uuid4(),
                                        "farm_identifier": f"F-{name}", "created_at": now, "updated_at": now}])
        db.execute(user_farm.insert(), [{"id": uuid.uuid4(), "user_id": USER, "farm_id": FARM, "role_id": uuid.uuid4(),
                                         "is_active": True, "assigned_at": now, "created_at": now, "updated_at": now}])
        for fid, action in ((FARM, "create"), (FARM, "login"), (OTHER_FARM, "delete")):
            add_audit_log(db, user_id=USER, farm_id=fid, action=action, entity="bovine")
        db.commit()
        yield db


def test_audit_read_model_joins_names_and_isolates_farms(audit_db: Any) -> None:
    service = AuditService(AuditRepository(audit_db))

    page = service.list_audit_logs(current_user_id=USER, filters=AuditLogFilters())

    assert page.total == 2  # la finca ajena no aparece
    assert {r.action for r in page.items} == {"create", "login"}
    assert {(r.user_full_name, r.user_email, r.farm_name) for r in page.items} == {("Ana Ruiz", "ana@x.com", "La Esperanza")}


def test_audit_foreign_farm_filter_returns_nothing(audit_db: Any) -> None:
    service = AuditService(AuditRepository(audit_db))

    page = service.list_audit_logs(current_user_id=USER, filters=AuditLogFilters(farm_id=OTHER_FARM))

    assert (page.total, page.items) == (0, [])


def test_audit_catalog_and_farm_logs(audit_db: Any) -> None:
    service = AuditService(AuditRepository(audit_db))

    assert service.catalog(USER) == {"actions": ["create", "login"], "entities": ["bovine"]}
    farm_logs = service.farm_logs(FARM)
    assert [r.action for r in farm_logs] == ["create"]  # sin eventos de sesión
    assert farm_logs[0].user_full_name == "Ana Ruiz"


# ═══════════════════════════════════════════════════════════════
# Servicio: exportación
# ═══════════════════════════════════════════════════════════════


def test_audit_export_rules() -> None:
    repo = MagicMock()
    repo.accessible_farm_ids.return_value = []
    service = AuditService(repo)

    with pytest.raises(BusinessRuleError) as exc:
        service.export(AuditExportFormat.JSON, current_user_id=USER, filters=AuditLogFilters())
    assert exc.value.message == JSON_EXPORT_NOT_ALLOWED

    csv_bytes = service.export(AuditExportFormat.CSV, current_user_id=USER, filters=AuditLogFilters())
    xlsx_bytes = service.export(AuditExportFormat.EXCEL, current_user_id=USER, filters=AuditLogFilters())
    assert csv_bytes.startswith("﻿".encode()) and xlsx_bytes[:2] == b"PK"


# ═══════════════════════════════════════════════════════════════
# Frontera HTTP
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
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, dict[str, bool]]]:
    from app.core.database import get_db
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.audit import dependencies as audit_deps

    allowed = {"value": True}
    monkeypatch.setattr(audit_deps, "has_permission_anywhere", lambda db, user_id, module, action: allowed["value"])
    repo = MagicMock()
    repo.accessible_farm_ids.return_value = []
    repo.farm_logs.return_value = []
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    app.dependency_overrides[audit_deps.get_audit_service] = lambda: AuditService(repo)
    try:
        yield TestClient(app), allowed
    finally:
        app.dependency_overrides.clear()


def test_http_system_audit_requires_permission_somewhere(client: tuple[TestClient, dict[str, bool]]) -> None:
    http, allowed = client

    assert http.get("/api/v1/admin/audit-logs").json() == {"total": 0, "limit": 100, "offset": 0, "items": []}
    allowed["value"] = False
    denied = http.get("/api/v1/admin/audit-logs")
    assert (denied.status_code, denied.json()) == (403, {"detail": "No tienes permiso para consultar la auditoría del sistema"})


def test_http_json_export_is_400(client: tuple[TestClient, dict[str, bool]]) -> None:
    http, _ = client

    response = http.get("/api/v1/admin/audit-logs/export", params={"export": "json"})

    assert (response.status_code, response.json()) == (400, {"detail": JSON_EXPORT_NOT_ALLOWED})


def test_http_farm_audit_route_lives_in_audit_module(client: tuple[TestClient, dict[str, bool]]) -> None:
    http, _ = client

    assert http.get(f"/api/v1/farms/{FARM}/audit-logs").json() == []


def test_audit_module_boots_like_uvicorn() -> None:
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-c", "import app.modules.audit; import app.main"],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr[-1500:]
