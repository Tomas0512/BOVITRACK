"""
Pruebas de la Parte 3c del refactor: módulos inventory y health.

¿Qué? Servicios con repositorios y colaboradores falsos; el repositorio de
      inventario contra la tabla `food` real en SQLite; los puertos que cada
      módulo OFRECE a otros (stock bajo, alimento de la finca, alertas
      sanitarias); y la frontera HTTP.
¿Para qué? Demostrar el contrato de cada README.md: el stock nunca queda
           negativo, cada cambio deja su movimiento, y los planes recalculan
           su próxima fecha.
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

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.health.models import SanitaryPlan
from app.modules.health.schemas import SanitaryPlanUpdate, TreatmentCreate
from app.modules.health.service import (
    BOVINE_NOT_IN_FARM,
    FOOD_NOT_IN_FARM,
    PLOT_NOT_IN_FARM,
    SanitaryPlanService,
    TreatmentService,
)
from app.modules.inventory.models import Food, StockMovement
from app.modules.inventory.schemas import ConsumptionCreate
from app.modules.inventory.service import (
    FOOD_NOT_FOUND,
    PADDOCK_NOT_IN_FARM,
    PADDOCK_OTHER_PLOT,
    InventoryService,
)
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import BovineRef, PaddockRef

FARM = uuid.uuid4()
USER = uuid.uuid4()
PLOT = uuid.uuid4()
PADDOCK = uuid.uuid4()
NOW = datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc)


# ═══════════════════════════════════════════════════════════════
# inventory
# ═══════════════════════════════════════════════════════════════


class FakeInventoryRepo:
    def __init__(self, *foods: Food) -> None:
        self.foods = {f.id: f for f in foods}
        self.added: list[Any] = []
        self.events: list[str] = []

    def get_food_in_farm(self, farm_id: uuid.UUID, food_id: uuid.UUID) -> Food | None:
        food = self.foods.get(food_id)
        return food if food is not None and food.farm_id == farm_id else None

    def add(self, row: Any) -> None:
        row.id = getattr(row, "id", None) or uuid.uuid4()
        self.added.append(row)
        self.events.append(f"add:{type(row).__name__}")

    def flush(self) -> None:
        self.events.append("flush")

    def commit(self) -> None:
        self.events.append("commit")

    def refresh(self, row: Any) -> None:
        self.events.append("refresh")


def _food(stock: str = "10", minimum: str | None = "5") -> Food:
    return Food(id=uuid.uuid4(), farm_id=FARM, name="Sal mineral", category="suplemento",
                unit_of_measure="kg", current_stock=Decimal(stock),
                min_stock_alert=Decimal(minimum) if minimum else None, is_active=True)


def _inventory(*foods: Food, paddock: PaddockRef | None = None) -> tuple[InventoryService, FakeInventoryRepo, MagicMock, MagicMock]:
    repo, scope, audit = FakeInventoryRepo(*foods), MagicMock(), MagicMock()
    service = InventoryService(
        repo,  # type: ignore[arg-type]
        ensure_farm_scope=scope,
        find_paddock=lambda farm_id, paddock_id: paddock if paddock and paddock_id == paddock.id else None,
        record_audit=audit,
    )
    return service, repo, scope, audit


def _consumption(food: Food, **overrides: Any) -> ConsumptionCreate:
    values: dict[str, Any] = {"food_id": food.id, "quantity": Decimal("3"), "feeding_date": NOW}
    values.update(overrides)
    return ConsumptionCreate(**values)


def test_inventory_consumption_discounts_stock_and_records_movement() -> None:
    food = _food("10")
    service, repo, scope, _ = _inventory(food)

    service.create_consumption(FARM, _consumption(food), USER)

    assert food.current_stock == Decimal("7")
    movement = next(r for r in repo.added if isinstance(r, StockMovement))
    assert (movement.quantity, movement.stock_before, movement.stock_after) == (Decimal("-3"), Decimal("10"), Decimal("7"))
    assert movement.movement_type == "consumption"
    scope.assert_called_once_with(FARM, bovine_id=None, land_plot_id=None)


def test_inventory_consumption_never_leaves_negative_stock() -> None:
    food = _food("2")
    service, repo, _, _ = _inventory(food)

    with pytest.raises(BusinessRuleError) as exc:
        service.create_consumption(FARM, _consumption(food, quantity=Decimal("3")), USER)
    assert exc.value.message == "Stock insuficiente. Disponible: 2 kg"
    assert food.current_stock == Decimal("2") and repo.added == []


@pytest.mark.parametrize(
    ("paddock", "overrides", "message"),
    [
        (None, {"paddock_id": PADDOCK}, PADDOCK_NOT_IN_FARM),
        (PaddockRef(PADDOCK, uuid.uuid4()), {"paddock_id": PADDOCK, "land_plot_id": PLOT}, PADDOCK_OTHER_PLOT),
    ],
)
def test_inventory_consumption_validates_paddock(paddock: PaddockRef | None, overrides: dict[str, Any], message: str) -> None:
    food = _food()
    service, _, _, _ = _inventory(food, paddock=paddock)

    with pytest.raises(BusinessRuleError) as exc:
        service.create_consumption(FARM, _consumption(food, **overrides), USER)
    assert exc.value.message == message


def test_inventory_consumption_takes_land_plot_from_paddock() -> None:
    food = _food()
    service, _, _, _ = _inventory(food, paddock=PaddockRef(PADDOCK, PLOT))

    consumption = service.create_consumption(FARM, _consumption(food, paddock_id=PADDOCK), USER)

    assert consumption.land_plot_id == PLOT


def test_inventory_food_of_another_farm_is_404() -> None:
    service, _, _, _ = _inventory()

    with pytest.raises(NotFoundError) as exc:
        service.get_food(FARM, uuid.uuid4())
    assert exc.value.message == FOOD_NOT_FOUND


def test_inventory_purchase_adds_stock_and_sets_cost() -> None:
    food = _food("10")
    service, _, _, audit = _inventory(food)

    _, movement = service.record_purchase(FARM, food.id, Decimal("5"), Decimal("2000"), USER)

    assert food.current_stock == Decimal("15") and food.cost_per_unit == Decimal("2000")
    assert (movement.total_cost, movement.stock_before, movement.stock_after) == (Decimal("10000"), Decimal("10"), Decimal("15"))
    assert audit.call_args.kwargs["details"]["type"] == "purchase"


def test_inventory_adjustment_cannot_go_below_zero() -> None:
    food = _food("4")
    service, _, _, _ = _inventory(food)

    with pytest.raises(BusinessRuleError):
        service.record_stock_adjustment(FARM, food.id, Decimal("-5"), "inventario físico", USER)
    assert food.current_stock == Decimal("4")


def test_inventory_provided_ports_against_real_table() -> None:
    """build_low_stock_lookup y build_food_lookup: lo que inventario ofrece a otros módulos."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.modules import inventory

    engine = create_engine("sqlite://")
    Food.__table__.create(engine)
    with Session(engine) as db:
        rows = [_food("1", "5"), _food("3", "5"), _food("9", "5"), _food("0", None)]
        rows[1].name = "Melaza"
        other_farm = _food("0", "5")
        other_farm.farm_id = uuid.uuid4()
        db.add_all([*rows, other_farm])
        db.commit()

        low = inventory.build_low_stock_lookup(db)(FARM)
        exists = inventory.build_food_lookup(db)

        assert [item.current_stock for item in low] == [Decimal("1"), Decimal("3")]  # menor stock primero
        assert low[1].name == "Melaza" and low[0].unit_of_measure == "kg"
        assert exists(FARM, rows[0].id) is True
        assert exists(FARM, other_farm.id) is False


# ═══════════════════════════════════════════════════════════════
# health
# ═══════════════════════════════════════════════════════════════

COW = uuid.uuid4()
FOOD_ID = uuid.uuid4()


def _treatments() -> tuple[TreatmentService, MagicMock, MagicMock]:
    repo, audit = MagicMock(), MagicMock()
    service = TreatmentService(
        repo,
        find_bovine=lambda farm_id, bovine_id: BovineRef(bovine_id, "hembra") if bovine_id == COW else None,
        land_plot_exists=lambda farm_id, plot_id: plot_id == PLOT,
        food_exists=lambda farm_id, food_id: food_id == FOOD_ID,
        record_audit=audit,
    )
    return service, repo, audit


def _treatment(**overrides: Any) -> TreatmentCreate:
    values: dict[str, Any] = {"treatment_type": "vacuna", "product_name": "Aftosa", "dose": "2 mL",
                              "administration_route": "intramuscular", "application_date": NOW, "bovine_id": COW}
    values.update(overrides)
    return TreatmentCreate(**values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"bovine_id": uuid.uuid4()}, BOVINE_NOT_IN_FARM),
        ({"bovine_id": None, "land_plot_id": uuid.uuid4()}, PLOT_NOT_IN_FARM),
        ({"food_id": uuid.uuid4()}, FOOD_NOT_IN_FARM),
    ],
)
def test_health_treatment_references_must_belong_to_farm(overrides: dict[str, Any], message: str) -> None:
    service, repo, _ = _treatments()

    with pytest.raises(BusinessRuleError) as exc:
        service.create_treatment(FARM, _treatment(**overrides), USER)
    assert exc.value.message == message
    repo.add.assert_not_called()


def test_health_treatment_is_saved_and_audited() -> None:
    service, repo, audit = _treatments()

    treatment = service.create_treatment(FARM, _treatment(food_id=FOOD_ID), USER)

    assert treatment.applied_by == USER and treatment.food_id == FOOD_ID
    repo.add.assert_called_once_with(treatment)
    assert audit.call_args.kwargs["details"] == {"type": "vacuna"}


def _plan(**overrides: Any) -> SanitaryPlan:
    values: dict[str, Any] = {"id": uuid.uuid4(), "farm_id": FARM, "bovine_id": COW, "land_plot_id": None,
                              "vaccine_or_treatment_name": "Aftosa", "treatment_type": "vacuna",
                              "administration_route": "intramuscular", "frequency_days": 180, "is_active": True}
    values.update(overrides)
    return SanitaryPlan(**values)


def test_health_apply_plan_schedules_next_date_from_today() -> None:
    plan = _plan()
    repo = MagicMock()
    repo.get_in_farm.return_value = plan
    service = SanitaryPlanService(repo, MagicMock(), MagicMock(), now=lambda: NOW)

    service.mark_as_applied(FARM, plan.id, USER)

    assert plan.last_applied_date == NOW
    assert plan.next_scheduled_date == NOW + timedelta(days=180)


def test_health_update_plan_revalidates_scope_and_keeps_target() -> None:
    plan = _plan()
    repo, scope = MagicMock(), MagicMock()
    repo.get_in_farm.return_value = plan
    service = SanitaryPlanService(repo, scope, MagicMock())

    service.update_sanitary_plan(FARM, plan.id, SanitaryPlanUpdate(frequency_days=90), USER)

    # SanitaryPlanUpdate no permite cambiar bovino ni lote: se revalidan los que ya tenía.
    scope.assert_called_once_with(FARM, bovine_id=COW, land_plot_id=None)
    assert plan.frequency_days == 90


def test_health_missing_plan_is_404() -> None:
    repo = MagicMock()
    repo.get_in_farm.return_value = None
    service = SanitaryPlanService(repo, MagicMock(), MagicMock())

    with pytest.raises(NotFoundError) as exc:
        service.get_sanitary_plan(FARM, uuid.uuid4())
    assert exc.value.message == "Plan sanitario no encontrado"


def test_health_provided_sanitary_alerts_return_dtos() -> None:
    """build_sanitary_alerts: lo que salud ofrece a notifications (DTOs, no modelos ORM)."""
    from app.modules import health
    from app.shared.ports import SanitaryDue

    overdue_plan = _plan(next_scheduled_date=date(2026, 11, 1))
    source = health.build_sanitary_alerts(MagicMock())
    source._repo = MagicMock()  # type: ignore[attr-defined]
    source._repo.overdue.return_value = [overdue_plan]  # type: ignore[attr-defined]
    source._repo.upcoming.return_value = []  # type: ignore[attr-defined]

    due = source.overdue(FARM, NOW)

    assert due == [SanitaryDue(overdue_plan.id, "Aftosa", "vacuna", date(2026, 11, 1), COW, None)]
    assert source.upcoming(FARM, NOW, NOW + timedelta(days=7)) == []


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
def client() -> Iterator[TestClient]:
    from app.core.database import get_db
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.health.dependencies import get_treatment_service
    from app.modules.inventory.dependencies import get_inventory_service

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    app.dependency_overrides[get_inventory_service] = lambda: _inventory(_food("2"))[0]
    app.dependency_overrides[get_treatment_service] = lambda: _treatments()[0]
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_http_inventory_errors(client: TestClient) -> None:
    base = f"/api/v1/farms/{FARM}/food"

    missing = client.get(f"{base}/{uuid.uuid4()}")
    assert (missing.status_code, missing.json()) == (404, {"detail": FOOD_NOT_FOUND})

    bad_qty = client.post(f"{base}/consumptions", json={"food_id": str(uuid.uuid4()), "quantity": "0",
                                                         "feeding_date": NOW.isoformat()})
    assert bad_qty.status_code == 422


def test_http_treatment_rule_is_400(client: TestClient) -> None:
    response = client.post(f"/api/v1/farms/{FARM}/treatments", json={
        "treatment_type": "vacuna", "product_name": "Aftosa", "dose": "2 mL",
        "administration_route": "intramuscular", "application_date": NOW.isoformat(),
        "bovine_id": str(uuid.uuid4()),
    })

    assert (response.status_code, response.json()) == (400, {"detail": BOVINE_NOT_IN_FARM})


def test_http_both_health_routers_are_mounted(client: TestClient) -> None:
    from app.main import app

    paths = {route.path for route in app.routes}  # type: ignore[attr-defined]
    assert "/api/v1/farms/{farm_id}/treatments" in paths
    assert "/api/v1/farms/{farm_id}/sanitary-plans/{plan_id}/apply" in paths


@pytest.mark.parametrize("entrypoint", ["app.modules.inventory", "app.modules.health"])
def test_module_boots_like_uvicorn(entrypoint: str) -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", f"import {entrypoint}; import app.main"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr[-1500:]
