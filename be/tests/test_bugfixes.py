"""
Pruebas de regresión de los bugs corregidos antes de la Parte 3c.

¿Qué? Una prueba por bug, que reproduce el escenario que antes fallaba:
      1. reports: fecha mal escrita respondía 500 -> ahora 422.
      2. tasks: editar no validaba la finca del bovino/lote (IDOR) -> ahora sí.
      3. tasks: status/priority aceptaban cualquier texto -> ahora solo valores válidos.
      4. milk_production: duplicados previos en la BD daban 500 -> ahora 400.
      5. economics: el promedio diario de un rango contaba un día de menos.
      6. documents: el archivo se borraba antes del commit -> ahora después.
      7. notifications: `total` del historial era el tamaño de la página.
¿Para qué? Que ninguno de estos bugs vuelva sin que una prueba falle.
"""

import uuid
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import TaskCreate, TaskUpdate
from app.modules.tasks.service import TaskService

FARM = uuid.uuid4()
USER = uuid.uuid4()


class _AllowAllSession:
    """Sesión falsa para require_permission: membresía activa y todos los permisos."""

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
def app_client() -> Iterator[tuple[TestClient, Any]]:
    from app.core.database import get_db
    from app.core.limiter import limiter
    from app.modules.identity import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    was_enabled, limiter.enabled = limiter.enabled, False
    try:
        yield TestClient(app), app
    finally:
        limiter.enabled = was_enabled
        app.dependency_overrides.clear()


# ── 1. reports: fecha inválida -> 422 ─────────────────────────────


@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_reports_malformed_date_is_422_not_500(app_client: tuple[TestClient, Any], field: str) -> None:
    from app.modules.reports.dependencies import get_report_service

    client, app = app_client
    app.dependency_overrides[get_report_service] = lambda: MagicMock()

    response = client.get(f"/api/v1/farms/{FARM}/reports", params={field: "2026-13-45"})

    assert response.status_code == 422
    assert response.json() == {"detail": f"Fecha inválida en '{field}': use el formato YYYY-MM-DD"}


# ── 2 y 3. tasks: alcance al editar y valores válidos ─────────────


class _TaskRepo:
    def __init__(self, task: Task) -> None:
        self.task = task

    def get_in_farm(self, farm_id: uuid.UUID, task_id: uuid.UUID) -> Task | None:
        return self.task if task_id == self.task.id else None

    def commit(self) -> None: ...

    def refresh(self, task: Task) -> None: ...


def _task() -> Task:
    return Task(id=uuid.uuid4(), farm_id=FARM, assigned_to=USER, assigned_by=USER, title="t",
                task_type="general", due_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
                status="pendiente", priority="media")


def test_tasks_update_rejects_bovine_of_another_farm() -> None:
    task = _task()

    def scope(farm_id: uuid.UUID, **refs: Any) -> None:
        raise PermissionError(f"fuera de la finca: {refs}")

    service = TaskService(_TaskRepo(task), scope, MagicMock())  # type: ignore[arg-type]

    with pytest.raises(PermissionError):
        service.update(FARM, task.id, TaskUpdate(bovine_id=uuid.uuid4()), USER)
    assert task.bovine_id is None  # no se aplicó el cambio


def test_tasks_update_without_references_does_not_check_scope() -> None:
    task = _task()
    scope = MagicMock()
    service = TaskService(_TaskRepo(task), scope, MagicMock())  # type: ignore[arg-type]

    service.update(FARM, task.id, TaskUpdate(status="en_progreso"), USER)

    scope.assert_not_called()
    assert task.status == "en_progreso"


def test_tasks_update_checks_new_land_plot() -> None:
    task = _task()
    scope = MagicMock()
    service = TaskService(_TaskRepo(task), scope, MagicMock())  # type: ignore[arg-type]
    plot = uuid.uuid4()

    service.update(FARM, task.id, TaskUpdate(land_plot_id=plot), USER)

    scope.assert_called_once_with(FARM, bovine_id=None, land_plot_id=plot)


@pytest.mark.parametrize(("field", "value"), [("status", "terminada"), ("priority", "urgentísima")])
def test_tasks_reject_unknown_status_and_priority(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        TaskUpdate(**{field: value})
    with pytest.raises(ValidationError):
        TaskCreate(assigned_to=USER, title="t", task_type="general",
                   due_date=datetime(2026, 12, 1, tzinfo=timezone.utc), **{field: value})


def test_tasks_invalid_status_is_422_over_http(app_client: tuple[TestClient, Any]) -> None:
    client, _ = app_client

    response = client.put(f"/api/v1/farms/{FARM}/tasks/{uuid.uuid4()}", json={"status": "terminada"})

    assert response.status_code == 422


# ── 4. milk_production: duplicados previos -> 400, no 500 ──────────


def test_milk_duplicate_check_survives_existing_duplicates() -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.modules.milk_production.models import MilkProduction
    from app.modules.milk_production.repository import MilkProductionRepository

    engine = create_engine("sqlite://")
    MilkProduction.__table__.create(engine)
    cow, day = uuid.uuid4(), datetime(2026, 11, 20, 6, 0)
    with Session(engine) as session:
        for _ in range(2):  # dos duplicados "viejos" ya guardados
            session.add(MilkProduction(farm_id=FARM, bovine_id=cow, quantity_liters=Decimal("5"),
                                       milking_date=day, milking_session="mañana", milking_type="manual",
                                       registered_by=USER))
        session.commit()

        repo = MilkProductionRepository(session)
        assert repo.exists_for_bovine_session(cow, day, "mañana") is True
        assert repo.exists_for_bovine_session(cow, day, "tarde") is False


# ── 5. economics: rango inclusivo ─────────────────────────────────


def test_economics_daily_average_counts_both_range_ends() -> None:
    from app.modules.economics.models import EconomicRecord
    from app.modules.economics.service import EconomicsService

    repo = MagicMock()
    repo.list_by_farm.return_value = [
        EconomicRecord(farm_id=FARM, record_type="ingreso", category="venta_leche",
                       amount=Decimal("70"), record_date=date(2026, 11, 3)),
    ]
    service = EconomicsService(repo, MagicMock(), today=lambda: date(2026, 11, 20))

    ind = service.get_indicators(FARM, date(2026, 11, 1), date(2026, 11, 7))

    assert ind.avg_income_per_day == Decimal("10")  # 70 / 7 días (antes dividía por 6)


# ── 6. documents: borrar el archivo DESPUÉS del commit ─────────────


def test_documents_failed_commit_keeps_the_file() -> None:
    from app.modules.documents.models import Document
    from app.modules.documents.service import DocumentService

    doc = Document(id=uuid.uuid4(), farm_id=FARM, stored_filename="abc.pdf", original_filename="a.pdf",
                   is_active=True)
    repo = MagicMock()
    repo.get_active_in_farm.return_value = doc
    repo.commit.side_effect = RuntimeError("BD caída")
    storage = MagicMock()
    service = DocumentService(repo, storage, MagicMock(), MagicMock())

    with pytest.raises(RuntimeError):
        service.delete_document(FARM, doc.id, USER)
    storage.delete.assert_not_called()


def test_documents_successful_delete_removes_file_after_commit() -> None:
    from app.modules.documents.models import Document
    from app.modules.documents.service import DocumentService

    order: list[str] = []
    doc = Document(id=uuid.uuid4(), farm_id=FARM, stored_filename="abc.pdf", original_filename="a.pdf",
                   is_active=True)
    repo = MagicMock()
    repo.get_active_in_farm.return_value = doc
    repo.commit.side_effect = lambda: order.append("commit")
    storage = MagicMock()
    storage.delete.side_effect = lambda name: order.append(f"delete:{name}")
    service = DocumentService(repo, storage, MagicMock(), MagicMock())

    service.delete_document(FARM, doc.id, USER)

    assert order == ["commit", "delete:abc.pdf"]


# ── 7. notifications: total real del historial ────────────────────


def test_notifications_history_total_is_the_real_count(app_client: tuple[TestClient, Any]) -> None:
    from app.modules.notifications.dependencies import get_notification_service
    from app.modules.notifications.models import NotificationLog
    from app.modules.notifications.service import NotificationService

    client, app = app_client
    repo = MagicMock()
    repo.list_history.return_value = [
        NotificationLog(id=uuid.uuid4(), farm_id=FARM, user_id=USER, type="sanitary", title="t", message="m",
                        channel="in_app", status="sent", reference_id="r", created_at=datetime.now()),
    ]
    repo.count_history.return_value = 42
    empty = MagicMock(return_value=[])
    sanitary = MagicMock()
    sanitary.overdue.return_value = sanitary.upcoming.return_value = []
    service = NotificationService(repo, sanitary, empty, empty, MagicMock(), MagicMock(),
                                  now=lambda: datetime.now() - timedelta(0))
    app.dependency_overrides[get_notification_service] = lambda: service

    response = client.get(f"/api/v1/farms/{FARM}/alerts/history", params={"limit": 1, "type": "sanitary"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert (len(body["items"]), body["total"], body["limit"]) == (1, 42, 1)
    repo.count_history.assert_called_once_with(USER, FARM, notif_type="sanitary", unread_only=False)


# ═══════════════════════════════════════════════════════════════
# Bugs corregidos con decisión del equipo
# ═══════════════════════════════════════════════════════════════


# ── 8. Reactivación: solo admins de las fincas del solicitante ─────


@pytest.fixture
def identity_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """BD SQLite con usuarios, roles, membresías y solicitudes reales."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.modules.identity.models import UserFarm
    from app.modules.team.models import ReactivationRequest
    from app.modules.identity.models import Role
    from app.modules.identity.models import User
    _ = monkeypatch
    engine = create_engine("sqlite://")
    for table in (User.__table__, Role.__table__, UserFarm.__table__, ReactivationRequest.__table__):
        table.create(engine)

    with Session(engine) as db:
        admin_role = Role(id=uuid.uuid4(), name="Administrador", is_active=True)
        employee_role = Role(id=uuid.uuid4(), name="Empleado", is_active=True)
        db.add_all([admin_role, employee_role])

        def user(name: str, active: bool = True) -> Any:
            u = User(id=uuid.uuid4(), first_name=name, last_name="X", document_type="CC",
                     document_number=str(uuid.uuid4())[:10], email=f"{name}@x.com", phone="300",
                     hashed_password="h", is_active=active)
            db.add(u)
            return u

        def member(u: Any, farm: uuid.UUID, role: Any, active: bool = True) -> None:
            db.add(UserFarm(user_id=u.id, farm_id=farm, role_id=role.id, is_active=active))

        farm_a, farm_b = uuid.uuid4(), uuid.uuid4()
        ana, beto = user("ana"), user("beto")                       # admins de A y de B
        rosa, sin_finca = user("rosa", False), user("solo", False)  # cuentas desactivadas
        member(ana, farm_a, admin_role)
        member(beto, farm_b, admin_role)
        member(rosa, farm_a, employee_role, active=False)           # fue miembro de A
        req_rosa = ReactivationRequest(id=uuid.uuid4(), user_id=rosa.id, status="pending")
        req_solo = ReactivationRequest(id=uuid.uuid4(), user_id=sin_finca.id, status="pending")
        db.add_all([req_rosa, req_solo])
        db.commit()
        from app.modules.identity.repository import MembershipDirectory
        from app.modules.team.repository import ReactivationRepository, Transaction
        from app.modules.team.service import ReactivationService

        service = ReactivationService(ReactivationRepository(db), MembershipDirectory(db), Transaction(db),
                                      record_audit=lambda **kw: None)
        yield SimpleNamespace(db=db, service=service, ana=ana, beto=beto, rosa=rosa, req_rosa=req_rosa, req_solo=req_solo)


def test_reactivation_admin_only_sees_requests_from_their_farms(identity_db: Any) -> None:
    d = identity_db
    seen_by_ana = d.service.list_pending(d.ana.id)
    seen_by_beto = d.service.list_pending(d.beto.id)

    assert [r.user_email for r in seen_by_ana] == ["rosa@x.com"]
    assert seen_by_beto == []  # antes veía TODAS las solicitudes del sistema


def test_reactivation_out_of_scope_is_404_and_changes_nothing(identity_db: Any) -> None:
    from app.shared.exceptions import NotFoundError

    d = identity_db
    for request_id in (d.req_rosa.id, d.req_solo.id):
        with pytest.raises(NotFoundError):  # 404
            d.service.approve(request_id, d.beto.id)
    with pytest.raises(NotFoundError):
        d.service.reject(d.req_rosa.id, d.beto.id)
    assert d.rosa.is_active is False and d.req_rosa.status == "pending"


def test_reactivation_admin_of_the_farm_can_approve(identity_db: Any) -> None:
    d = identity_db
    d.service.approve(d.req_rosa.id, d.ana.id)

    assert d.rosa.is_active is True and d.req_rosa.status == "approved"


# ── 9. Documentos: permiso propio "documentos" ────────────────────


class _OnlyModuleSession(_AllowAllSession):
    """Concede permisos solo para un módulo (lee el módulo pedido en la consulta)."""

    def __init__(self, module: str) -> None:
        self._module = module

    def execute(self, stmt: Any) -> SimpleNamespace:
        entity = stmt.column_descriptions[0]["entity"].__name__
        if entity == "Permission":
            asked = [v for k, v in stmt.compile().params.items() if k.startswith("module")]
            if asked != [self._module]:
                return SimpleNamespace(scalar_one_or_none=lambda: None)
        return super().execute(stmt)


@pytest.mark.parametrize(("granted", "expected"), [("documentos", 200), ("bovinos", 403)])
def test_documents_require_their_own_permission(app_client: tuple[TestClient, Any], granted: str, expected: int) -> None:
    from app.core.database import get_db
    from app.modules.documents.dependencies import get_document_service

    client, app = app_client
    service = MagicMock()
    service.list_documents.return_value = ([], 0)
    app.dependency_overrides[get_document_service] = lambda: service
    app.dependency_overrides[get_db] = lambda: _OnlyModuleSession(granted)

    response = client.get(f"/api/v1/farms/{FARM}/documents")

    assert response.status_code == expected


# ── 10. Alertas: tarea programada; el historial solo lee ──────────


def test_history_endpoint_no_longer_runs_the_engine(app_client: tuple[TestClient, Any]) -> None:
    from app.modules.notifications.dependencies import get_notification_service

    client, app = app_client
    service = MagicMock()
    service.list_notification_history.return_value = []
    service.count_notification_history.return_value = 0
    app.dependency_overrides[get_notification_service] = lambda: service

    assert client.get(f"/api/v1/farms/{FARM}/alerts/history").status_code == 200
    service.run_notification_cycle.assert_not_called()


def test_scheduler_runs_every_farm_and_survives_a_failing_one(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    from app.modules.notifications import scheduler

    farms = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    sessions: list[MagicMock] = []

    def session_factory() -> MagicMock:
        sessions.append(MagicMock())
        return sessions[-1]

    class _Service:
        async def run_notification_cycle(self, farm_id: uuid.UUID) -> int:
            if farm_id == farms[1]:
                raise RuntimeError("finca con datos corruptos")
            return 2

    monkeypatch.setattr(scheduler, "active_farm_ids", lambda db: farms)
    monkeypatch.setattr(scheduler, "build_notification_service", lambda db: _Service())

    created = asyncio.run(scheduler.run_cycle_for_all_farms(session_factory))

    assert created == 4  # 2 + (falla) + 2
    assert len(sessions) == 4  # una para listar fincas + una por finca
    assert all(s.close.called for s in sessions)
    sessions[2].rollback.assert_called_once()  # la finca que falló


def test_scheduler_can_be_disabled() -> None:
    from app.modules.notifications.scheduler import start_notification_scheduler

    assert start_notification_scheduler(0) is None


# ── 11. Reporte sanitario: tratamientos pendientes ────────────────


def test_sanitary_report_counts_pending_treatments_from_today() -> None:
    from app.modules.reports.service import ReportService

    repo = MagicMock()
    repo.treatments_by_type.return_value = {}
    repo.active_sanitary_plans.return_value = 0
    repo.pending_treatments.return_value = 5

    report = ReportService(repo, today=lambda: date(2026, 11, 20)).build_sanitary_report(FARM, None, None)

    assert report.pending_treatments == 5  # antes siempre 0
    repo.pending_treatments.assert_called_once_with(FARM, date(2026, 11, 20))


# ═══════════════════════════════════════════════════════════════
# Bugs de ganado encontrados en la Parte 3d
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def livestock_db() -> Iterator[Any]:
    """Tablas reales bovine y weight en SQLite (la sesión NO hace autoflush, como en producción)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.modules.livestock.models import Bovine, Weight

    engine = create_engine("sqlite://")
    for table in (Bovine.__table__, Weight.__table__):
        table.create(engine)
    with sessionmaker(bind=engine, autoflush=False)() as session:
        yield session


def _cow_with_weights(db: Any, *weights: tuple[int, str]) -> Any:
    from app.modules.livestock.models import Bovine, Weight

    cow = Bovine(id=uuid.uuid4(), farm_id=FARM, identification_number="W-1", sex="hembra",
                 birth_date=date(2026, 6, 1), entry_type="nacimiento", entry_date=date(2026, 6, 1),
                 registered_by=USER, is_active=True, current_weight=Decimal(weights[-1][1]))
    db.add(cow)
    for day, kg in weights:
        db.add(Weight(farm_id=FARM, bovine_id=cow.id, weight_kg=Decimal(kg), measured_at=date(2026, 11, day),
                      daily_gain=Decimal("1.50") if day > 1 else None, registered_by=USER))
    db.commit()
    return cow


# ── 12. Curva de peso de terneros: respondía 500 ──────────────────


def test_calf_weight_history_reads_daily_gain(livestock_db: Any) -> None:
    from app.modules.livestock.repository import BovineRepository, WeightRepository
    from app.modules.livestock.service import CalfService

    cow = _cow_with_weights(livestock_db, (1, "60"), (11, "75"))
    service = CalfService(BovineRepository(livestock_db), WeightRepository(livestock_db), MagicMock(),
                          today=lambda: date(2026, 11, 20))

    history = service.get_calf_weight_history(FARM, cow.id)

    # Antes: AttributeError ('Weight' no tiene daily_gain_kg) -> 500.
    ids = [w.id for w in sorted(cow.weights, key=lambda w: w.measured_at)]
    assert history == [
        {"id": ids[0], "date": "2026-11-01", "weight_kg": 60.0, "daily_gain_kg": None},
        {"id": ids[1], "date": "2026-11-11", "weight_kg": 75.0, "daily_gain_kg": 1.5},
    ]


# ── 13. Plan de alimentación: respondía 500 siempre ────────────────


@pytest.fixture
def feeding_client(app_client: tuple[TestClient, Any]) -> Iterator[TestClient]:
    from app.modules.inventory.dependencies import get_calf_feeding_service
    from app.modules.inventory.models import Food
    from app.modules.inventory.service import CalfFeedingService
    from app.shared.ports import BovineRef

    client, app = app_client
    food = Food(id=FOOD, farm_id=FARM, name="Concentrado")
    repo = MagicMock()
    repo.get_food_in_farm.side_effect = lambda farm_id, food_id: food if food_id == FOOD else None
    app.dependency_overrides[get_calf_feeding_service] = lambda: CalfFeedingService(
        repo, lambda farm_id, bovine_id: BovineRef(bovine_id, "macho"))
    yield client


FOOD = uuid.uuid4()


def test_feeding_plan_accepts_the_json_the_frontend_sends(feeding_client: TestClient) -> None:
    response = feeding_client.post(f"/api/v1/farms/{FARM}/calves/{uuid.uuid4()}/feeding-plan", json={
        "food_id": str(FOOD), "quantity_kg_per_day": 2.5, "start_date": "2026-11-20",
        "end_date": "2026-12-20", "notes": "Introducir concentrado gradualmente",
    })

    # Antes: start_date llegaba como texto y .isoformat() fallaba -> 500.
    assert response.status_code == 201, response.text
    body = response.json()
    assert (body["food_name"], body["start_date"], body["end_date"]) == ("Concentrado", "2026-11-20", "2026-12-20")


@pytest.mark.parametrize("payload", [
    {"food_id": str(FOOD), "quantity_kg_per_day": 2.5, "start_date": "no-es-fecha"},
    {"food_id": str(FOOD), "quantity_kg_per_day": 2.5, "start_date": "2026-11-20", "end_date": "2026-11-01"},
    {"quantity_kg_per_day": 2.5, "start_date": "2026-11-20"},
])
def test_feeding_plan_invalid_body_is_422(feeding_client: TestClient, payload: dict[str, Any]) -> None:
    response = feeding_client.post(f"/api/v1/farms/{FARM}/calves/{uuid.uuid4()}/feeding-plan", json=payload)

    assert response.status_code == 422


# ── 14. Borrar el último pesaje recalcula el peso actual ──────────


def test_deleting_latest_weight_restores_previous_weight(livestock_db: Any) -> None:
    from app.modules.livestock.repository import BovineRepository, WeightRepository
    from app.modules.livestock.service import WeightService

    cow = _cow_with_weights(livestock_db, (1, "60"), (11, "75"))
    weights = WeightRepository(livestock_db)
    latest = weights.latest(cow.id)
    service = WeightService(weights, BovineRepository(livestock_db), MagicMock())

    service.delete_weight(FARM, cow.id, latest.id, USER)

    # Antes quedaba 75 (el peso del pesaje borrado).
    assert cow.current_weight == Decimal("60")


def test_deleting_an_older_weight_keeps_current_weight(livestock_db: Any) -> None:
    from app.modules.livestock.repository import BovineRepository, WeightRepository
    from app.modules.livestock.service import WeightService

    cow = _cow_with_weights(livestock_db, (1, "60"), (11, "75"))
    weights = WeightRepository(livestock_db)
    oldest = weights.list_for_bovine(FARM, cow.id)[0]
    service = WeightService(weights, BovineRepository(livestock_db), MagicMock())

    service.delete_weight(FARM, cow.id, oldest.id, USER)

    assert cow.current_weight == Decimal("75")


# ── 22. Plan sanitario: una dosis de 51 a 100 caracteres daba 500 ───
# La API aceptaba cualquier largo, el modelo decía VARCHAR(100) y la BD tenía
# VARCHAR(50). Migración s2t3u4v5w6x7 + límites en el schema (422).


def test_sanitary_plan_dose_up_to_100_chars_is_accepted_and_longer_is_422() -> None:
    from pydantic import ValidationError

    from app.modules.health.models import SanitaryPlan
    from app.modules.health.schemas import SanitaryPlanCreate

    base = {"bovine_id": uuid.uuid4(), "vaccine_or_treatment_name": "Aftosa", "treatment_type": "vacuna",
            "administration_route": "intramuscular", "frequency_days": 180}
    long_dose = "2 mL por cada 50 kg de peso vivo, repetir a los 21 días"  # 56 caracteres
    assert SanitaryPlanCreate(**base, dose=long_dose).dose == long_dose
    with pytest.raises(ValidationError):
        SanitaryPlanCreate(**base, dose="x" * 101)
    with pytest.raises(ValidationError):
        SanitaryPlanCreate(**{**base, "administration_route": "y" * 51})

    # El schema nunca acepta más de lo que cabe en la columna.
    columns = SanitaryPlan.__table__.c
    assert (columns.dose.type.length, columns.administration_route.type.length) == (100, 50)


# ── 23. Curva de peso de terneros: seguía en 500 (faltaba el id) ──


def test_calf_weight_history_route_answers_with_every_point(livestock_db: Any) -> None:
    """La ruta arma WeightRecordResponse con cada punto; sin "id" fallaba con cualquier pesaje."""
    from app.modules.livestock.repository import BovineRepository, WeightRepository
    from app.modules.livestock.schemas import WeightRecordResponse
    from app.modules.livestock.service import CalfService

    cow = _cow_with_weights(livestock_db, (1, "60"), (11, "60"))
    max(cow.weights, key=lambda w: w.measured_at).daily_gain = Decimal("0")  # ganancia cero: es 0, no "sin dato"
    livestock_db.commit()
    service = CalfService(BovineRepository(livestock_db), WeightRepository(livestock_db), MagicMock(),
                          today=lambda: date(2026, 11, 20))

    points = [WeightRecordResponse(**record) for record in service.get_calf_weight_history(FARM, cow.id)]

    assert [(p.weight_kg, p.daily_gain_kg) for p in points] == [(60.0, None), (60.0, 0.0)]
    assert {p.id for p in points} == {w.id for w in cow.weights}
