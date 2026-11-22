"""
Pruebas de la Parte 3a del refactor: módulos economics, milk_production y reproduction.

¿Qué? Para cada módulo se prueba el servicio con repositorio y colaboradores
      falsos (sin BD), y luego la frontera HTTP: que los errores de dominio
      salgan con el código y el mensaje de siempre. Además, el adaptador real
      que registra crías se prueba contra la tabla `bovine` en SQLite.
¿Para qué? Demostrar que cada módulo cumple el contrato de su README.md y que
           el comportamiento es el mismo de antes del refactor.
¿Impacto? Si cambia una regla (gestación de 283 días, duplicados de ordeño,
          solo hembras paren...) o un mensaje de error, estas pruebas fallan.
"""

import uuid
from collections.abc import Iterator
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.economics.models import EconomicRecord
from app.modules.economics.schemas import EconomicRecordCreate
from app.modules.economics.service import RECORD_NOT_FOUND, EconomicsService
from app.modules.milk_production.models import MilkProduction
from app.modules.milk_production.schemas import MilkProductionCreate, MilkProductionUpdate
from app.modules.milk_production.service import (
    BOVINE_NOT_IN_FARM,
    DUPLICATE_MILKING,
    NEEDS_BOVINE_OR_PLOT,
    PLOT_NOT_IN_FARM,
    MilkProductionService,
)
from app.modules.reproduction.schemas import ReproductiveEventCreate, ReproductiveEventUpdate
from app.modules.reproduction.service import (
    BULL_NOT_IN_FARM,
    GESTATION_DAYS,
    ONLY_FEMALES_GIVE_BIRTH,
    ReproductionService,
)
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import BovineRef

FARM = uuid.uuid4()
OTHER_FARM = uuid.uuid4()
USER = uuid.uuid4()
COW = uuid.uuid4()
BULL = uuid.uuid4()
PLOT = uuid.uuid4()


# ═══════════════════════════════════════════════════════════════
# Dobles de prueba comunes
# ═══════════════════════════════════════════════════════════════


class FakeRepo:
    """Repositorio en memoria genérico: guarda filas y registra el orden de las llamadas."""

    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Any] = {}
        self.events: list[str] = []
        self.duplicate = False  # lo que responde exists_for_bovine_session

    def get_in_farm(self, farm_id: uuid.UUID, row_id: uuid.UUID) -> Any:
        row = self.rows.get(row_id)
        return row if row is not None and row.farm_id == farm_id else None

    def list_by_farm(self, farm_id: uuid.UUID, **_: Any) -> list[Any]:
        return [r for r in self.rows.values() if r.farm_id == farm_id]

    def exists_for_bovine_session(self, *args: Any, **kwargs: Any) -> bool:
        self.events.append("dup_check")
        return self.duplicate

    def add(self, row: Any) -> None:
        row.id = row.id or uuid.uuid4()
        self.rows[row.id] = row
        self.events.append("add")

    def delete(self, row: Any) -> None:
        self.rows.pop(row.id)
        self.events.append("delete")

    def commit(self) -> None:
        self.events.append("commit")

    def refresh(self, row: Any) -> None:
        now = datetime.now(timezone.utc)
        for attr in ("created_at", "updated_at"):
            if hasattr(type(row), attr) and getattr(row, attr, None) is None:
                setattr(row, attr, now)
        self.events.append("refresh")


class Recorder:
    """Colaborador falso: guarda las llamadas y devuelve un valor fijo."""

    def __init__(self, events: list[str] | None = None, name: str = "", returns: Any = None) -> None:
        self.calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self._events, self._name, self._returns = events, name, returns

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((args, kwargs))
        if self._events is not None:
            self._events.append(self._name)
        return self._returns() if callable(self._returns) else self._returns


def herd(**bovines: str) -> Any:
    """BovineLookup falso: {id: sexo} de los bovinos que existen en FARM."""
    index = {uuid.UUID(k) if not isinstance(k, uuid.UUID) else k: v for k, v in bovines.items()}

    def find(farm_id: uuid.UUID, bovine_id: uuid.UUID) -> BovineRef | None:
        sex = index.get(bovine_id)
        return BovineRef(id=bovine_id, sex=sex) if farm_id == FARM and sex else None

    return find


# ═══════════════════════════════════════════════════════════════
# economics
# ═══════════════════════════════════════════════════════════════


def _econ(today: date = date(2026, 11, 15)) -> tuple[EconomicsService, FakeRepo, Recorder]:
    repo = FakeRepo()
    audit = Recorder(repo.events, "audit")
    return EconomicsService(repo, audit, today=lambda: today), repo, audit  # type: ignore[arg-type]


def _record(record_type: str, category: str, amount: str, day: date) -> EconomicRecord:
    return EconomicRecord(
        id=uuid.uuid4(), farm_id=FARM, record_type=record_type, category=category,
        amount=Decimal(amount), record_date=day, registered_by=USER,
    )


def test_economics_create_saves_then_audits_with_amount_as_text() -> None:
    service, repo, audit = _econ()
    data = EconomicRecordCreate(record_type="ingreso", category="venta_leche", amount=Decimal("150.50"), record_date=date(2026, 11, 1))

    record = service.create_record(FARM, data, USER)

    assert record.registered_by == USER
    assert repo.events == ["add", "commit", "refresh", "audit", "commit"]
    assert audit.calls[0][1]["details"] == {"type": "ingreso", "amount": "150.50", "category": "venta_leche"}


def test_economics_record_of_another_farm_is_not_found() -> None:
    service, repo, _ = _econ()
    foreign = _record("ingreso", "venta_leche", "1", date(2026, 1, 1))
    foreign.farm_id = OTHER_FARM
    repo.rows[foreign.id] = foreign

    with pytest.raises(NotFoundError) as exc:
        service.get_record(FARM, foreign.id)
    assert exc.value.message == RECORD_NOT_FOUND


def test_economics_indicators_balance_month_and_categories() -> None:
    service, repo, _ = _econ(today=date(2026, 11, 15))
    for r in (
        _record("ingreso", "venta_leche", "100", date(2026, 11, 2)),   # este mes
        _record("ingreso", "venta_animal", "300", date(2026, 10, 5)),  # mes pasado
        _record("egreso", "compra_insumo", "50", date(2026, 11, 10)),       # este mes
    ):
        repo.rows[r.id] = r

    ind = service.get_indicators(FARM)

    assert ind.total_income == Decimal("400") and ind.total_expense == Decimal("50")
    assert ind.balance == Decimal("350")
    assert ind.monthly_income == Decimal("100") and ind.monthly_expense == Decimal("50")
    assert ind.income_by_category == {"venta_leche": Decimal("100"), "venta_animal": Decimal("300")}
    # Sin rango: días entre el primer y el último movimiento, inclusive (5 oct - 10 nov = 37).
    assert ind.avg_income_per_day == Decimal("400") / Decimal("37")


def test_economics_indicators_with_range_divide_by_range_days() -> None:
    service, repo, _ = _econ()
    r = _record("ingreso", "venta_leche", "100", date(2026, 11, 2))
    repo.rows[r.id] = r

    # Rango inclusivo: del 1 al 10 de noviembre son 10 días.
    ind = service.get_indicators(FARM, date(2026, 11, 1), date(2026, 11, 10))

    assert ind.avg_income_per_day == Decimal("10")


# ═══════════════════════════════════════════════════════════════
# milk_production
# ═══════════════════════════════════════════════════════════════


def _milk(plot_exists: bool = True) -> tuple[MilkProductionService, FakeRepo, Recorder]:
    repo = FakeRepo()
    audit = Recorder(repo.events, "audit")
    service = MilkProductionService(
        repo,  # type: ignore[arg-type]
        find_bovine=herd(**{str(COW): "hembra"}),
        land_plot_exists=lambda farm_id, plot_id: plot_exists and farm_id == FARM and plot_id == PLOT,
        record_audit=audit,
    )
    return service, repo, audit


def _milking(**overrides: Any) -> MilkProductionCreate:
    values: dict[str, Any] = {
        "bovine_id": COW,
        "quantity_liters": Decimal("12.5"),
        "milking_date": datetime(2026, 11, 20, 6, 0, tzinfo=timezone.utc),
        "milking_session": "mañana",
        "milking_type": "manual",
    }
    values.update(overrides)
    return MilkProductionCreate(**values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"bovine_id": None, "land_plot_id": None}, NEEDS_BOVINE_OR_PLOT),
        ({"bovine_id": uuid.uuid4()}, BOVINE_NOT_IN_FARM),
        ({"bovine_id": None, "land_plot_id": uuid.uuid4()}, PLOT_NOT_IN_FARM),
    ],
)
def test_milk_create_rejects_invalid_references(overrides: dict[str, Any], message: str) -> None:
    service, repo, _ = _milk()

    with pytest.raises(BusinessRuleError) as exc:
        service.create_record(FARM, _milking(**overrides), USER)
    assert exc.value.message == message
    assert repo.rows == {}


def test_milk_create_rejects_duplicate_bovine_date_session() -> None:
    service, repo, _ = _milk()
    repo.duplicate = True

    with pytest.raises(BusinessRuleError) as exc:
        service.create_record(FARM, _milking(), USER)
    assert exc.value.message == DUPLICATE_MILKING


def test_milk_create_by_land_plot_skips_duplicate_check() -> None:
    service, repo, audit = _milk()

    service.create_record(FARM, _milking(bovine_id=None, land_plot_id=PLOT), USER)

    assert "dup_check" not in repo.events
    assert audit.calls[0][1]["details"] == {"liters": "12.5"}


def test_milk_update_cannot_leave_record_without_bovine_or_plot() -> None:
    service, repo, _ = _milk()
    record = service.create_record(FARM, _milking(), USER)

    with pytest.raises(BusinessRuleError) as exc:
        service.update_record(FARM, record.id, MilkProductionUpdate(bovine_id=None), USER)
    assert exc.value.message == NEEDS_BOVINE_OR_PLOT


def test_milk_summary_totals_and_top_bovines() -> None:
    service, repo, _ = _milk()
    day1 = datetime(2026, 11, 20, 6, tzinfo=timezone.utc)
    day2 = datetime(2026, 11, 21, 6, tzinfo=timezone.utc)
    for liters, day, session in (("10", day1, "mañana"), ("5", day1, "tarde"), ("15", day2, None)):
        row = MilkProduction(id=uuid.uuid4(), farm_id=FARM, bovine_id=COW, quantity_liters=Decimal(liters),
                             milking_date=day, milking_session=session, milking_type="manual")
        repo.rows[row.id] = row

    summary = service.get_milk_summary(FARM)

    assert summary["total_liters"] == "30"
    assert summary["milking_days"] == 2 and summary["avg_daily_liters"] == "15.00"
    assert summary["by_session"] == {"mañana": "10", "tarde": "5", "sin_sesión": "15"}
    assert summary["top_bovines"] == [{"bovine_id": str(COW), "total_liters": "30"}]


def test_milk_summary_empty() -> None:
    service, _, _ = _milk()

    assert service.get_milk_summary(FARM)["total_liters"] == "0"


# ═══════════════════════════════════════════════════════════════
# reproduction
# ═══════════════════════════════════════════════════════════════


def _repro(**bovines: str) -> tuple[ReproductionService, FakeRepo, Recorder, Recorder, Recorder]:
    repo = FakeRepo()
    scope = Recorder()
    calves = Recorder(repo.events, "calf", returns=uuid.uuid4)
    audit = Recorder(repo.events, "audit")
    service = ReproductionService(
        repo,  # type: ignore[arg-type]
        find_bovine=herd(**(bovines or {str(COW): "hembra", str(BULL): "macho"})),
        ensure_farm_scope=scope,
        register_calf=calves,
        record_audit=audit,
    )
    return service, repo, scope, calves, audit


def _event(**overrides: Any) -> ReproductiveEventCreate:
    values: dict[str, Any] = {"bovine_id": COW, "event_type": "servicio", "event_date": date(2026, 3, 1)}
    values.update(overrides)
    return ReproductiveEventCreate(**values)


def test_reproduction_service_gets_due_date_after_283_days() -> None:
    service, _, _, _, _ = _repro()

    event = service.create_event(FARM, _event(bull_id=BULL), USER)

    assert GESTATION_DAYS == 283
    assert event.due_date == date(2026, 12, 9)


def test_reproduction_only_females_give_birth() -> None:
    service, _, _, _, _ = _repro()

    with pytest.raises(BusinessRuleError) as exc:
        service.create_event(FARM, _event(bovine_id=BULL, event_type="parto", result="macho"), USER)
    assert exc.value.message == ONLY_FEMALES_GIVE_BIRTH


def test_reproduction_bull_must_belong_to_farm() -> None:
    service, _, _, _, _ = _repro()

    with pytest.raises(BusinessRuleError) as exc:
        service.create_event(FARM, _event(bull_id=uuid.uuid4()), USER)
    assert exc.value.message == BULL_NOT_IN_FARM


def test_reproduction_twins_register_two_calves_before_saving_event() -> None:
    service, repo, _, calves, _ = _repro()

    event = service.create_event(FARM, _event(event_type="parto", result="gemelos", event_date=date(2026, 9, 5)), USER)

    prefix = str(COW)[:6]
    assert [(c[1]["sex"], c[1]["identification_number"]) for c in calves.calls] == [
        ("macho", f"CRIA-{prefix}-20260905-1"),
        ("hembra", f"CRIA-{prefix}-20260905-2"),
    ]
    assert all(c[1]["mother_id"] == COW and c[1]["birth_date"] == date(2026, 9, 5) for c in calves.calls)
    assert event.calf_id is not None
    # Las crías se registran antes de guardar el evento (misma transacción).
    assert repo.events[:3] == ["calf", "calf", "add"]


def test_reproduction_birth_without_known_result_creates_no_calves() -> None:
    service, _, _, calves, _ = _repro()

    event = service.create_event(FARM, _event(event_type="parto", result="negativo"), USER)

    assert calves.calls == [] and event.calf_id is None


def test_reproduction_update_checks_scope_and_creates_calf_when_becoming_birth() -> None:
    service, _, scope, calves, _ = _repro()
    event = service.create_event(FARM, _event(event_type="diagnostico_gestion"), USER)

    service.update_event(FARM, event.id, ReproductiveEventUpdate(event_type="parto", result="hembra", bull_id=BULL), USER)

    assert scope.calls == [((FARM,), {"bovine_id": BULL})]
    assert len(calves.calls) == 1 and event.calf_id is not None


def test_reproduction_missing_event_is_not_found() -> None:
    service, _, _, _, _ = _repro()

    with pytest.raises(NotFoundError):
        service.get_event(FARM, uuid.uuid4())


def test_calf_registrar_adapter_creates_bovine_and_audits(monkeypatch: pytest.MonkeyPatch) -> None:
    """El adaptador real (livestock.build_calf_registrar) contra la tabla `bovine` en SQLite."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.modules import livestock
    from app.modules.livestock import dependencies as livestock_deps
    from app.modules.livestock.models import Bovine

    audits: list[dict[str, Any]] = []
    monkeypatch.setattr(livestock_deps, "add_audit_log", lambda db, **kw: audits.append(kw))
    engine = create_engine("sqlite://")
    Bovine.__table__.create(engine)

    with Session(engine) as session:
        calf_id = livestock.build_calf_registrar(session)(
            FARM, identification_number="CRIA-abc", sex="hembra",
            birth_date=date(2026, 5, 1), mother_id=COW, registered_by=USER,
        )
        calf = session.get(Bovine, calf_id)

    assert calf is not None
    assert (calf.sex, calf.entry_type, calf.birth_date, calf.entry_date, calf.mother_id) == (
        "hembra", "nacimiento", date(2026, 5, 1), date(2026, 5, 1), COW,
    )
    assert audits == [{
        "user_id": str(USER), "farm_id": str(FARM), "action": "create", "entity": "bovine",
        "entity_id": str(calf_id), "details": {"calf_from": "parto", "mother_id": str(COW)},
    }]


# ═══════════════════════════════════════════════════════════════
# Frontera HTTP de los tres módulos
# ═══════════════════════════════════════════════════════════════


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
def client() -> Iterator[TestClient]:
    from app.core.database import get_db
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.economics.dependencies import get_economics_service
    from app.modules.milk_production.dependencies import get_milk_production_service
    from app.modules.reproduction.dependencies import get_reproduction_service

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    app.dependency_overrides[get_economics_service] = lambda: _econ()[0]
    app.dependency_overrides[get_milk_production_service] = lambda: _milk()[0]
    app.dependency_overrides[get_reproduction_service] = lambda: _repro()[0]
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("path", "detail"),
    [
        ("economics", "Registro economico no encontrado"),
        ("milk-production", "Registro de producción no encontrado"),
        ("reproductive-events", "Evento reproductivo no encontrado"),
    ],
)
def test_http_not_found_keeps_original_messages(client: TestClient, path: str, detail: str) -> None:
    response = client.get(f"/api/v1/farms/{FARM}/{path}/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": detail}


def test_http_business_rules_answer_400(client: TestClient) -> None:
    milk = client.post(f"/api/v1/farms/{FARM}/milk-production", json={
        "quantity_liters": "10", "milking_date": "2026-11-20T06:00:00Z", "milking_type": "manual",
    })
    birth = client.post(f"/api/v1/farms/{FARM}/reproductive-events", json={
        "bovine_id": str(BULL), "event_type": "parto", "event_date": "2026-09-01", "result": "macho",
    })

    assert (milk.status_code, milk.json()) == (400, {"detail": NEEDS_BOVINE_OR_PLOT})
    assert (birth.status_code, birth.json()) == (400, {"detail": ONLY_FEMALES_GIVE_BIRTH})


def test_http_create_returns_201(client: TestClient) -> None:
    response = client.post(f"/api/v1/farms/{FARM}/economics", json={
        "record_type": "egreso", "category": "compra_insumo", "amount": "20", "record_date": "2026-11-01",
    })

    assert response.status_code == 201
    assert response.json()["registered_by"] == str(USER)


@pytest.mark.parametrize("entrypoint", ["app.modules.economics", "app.modules.milk_production", "app.modules.reproduction"])
def test_module_boots_like_uvicorn(entrypoint: str) -> None:
    """Importar el módulo primero (como haría Alembic o un script) no debe crear ciclos."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", f"import {entrypoint}; import app.main"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr[-1500:]
