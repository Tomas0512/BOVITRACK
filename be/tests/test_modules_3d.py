"""
Pruebas de la Parte 3d del refactor: módulo livestock (bovinos, pesajes,
terneros, movimientos) y el plan de alimentación que pasó a inventory.

¿Qué? Servicios con repositorios y colaboradores falsos; repositorios contra
      las tablas reales `bovine` y `weight` en SQLite; los puertos que ganado
      ofrece a otros módulos; y la frontera HTTP.
¿Para qué? Demostrar el contrato del README.md de livestock y que el cambio de
           estructura no alteró reglas: unicidad de identificación, coherencia
           lote/potrero, ganancia diaria, inmutabilidad de movimientos.
"""

import uuid
from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.livestock.models import AnimalMovement, Bovine, Weight
from app.modules.livestock.schemas import BovineCreate, BovineUpdate, MovementCreate, WeightCreate
from app.modules.livestock.service import BovineService, CalfService, MovementService, WeightService
from app.modules.livestock.service import bovines as bovines_mod
from app.modules.livestock.service import calves as calves_mod
from app.modules.livestock.service import movements as movements_mod
from app.modules.livestock.service.weights import daily_gain
from app.shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError
from app.shared.ports import BovineRef, PaddockRef

FARM = uuid.uuid4()
USER = uuid.uuid4()
PLOT = uuid.uuid4()
OTHER_PLOT = uuid.uuid4()
PADDOCK = uuid.uuid4()
TODAY = date(2026, 11, 20)


def _bovine(**overrides: Any) -> Bovine:
    values: dict[str, Any] = {
        "id": uuid.uuid4(), "farm_id": FARM, "identification_number": "BT-1", "sex": "hembra",
        "birth_date": date(2026, 6, 1), "entry_type": "nacimiento", "entry_date": date(2026, 6, 1),
        "registered_by": USER, "is_active": True, "status": "activo",
    }
    values.update(overrides)
    return Bovine(**values)


# ═══════════════════════════════════════════════════════════════
# Bovinos
# ═══════════════════════════════════════════════════════════════


class FakeBovineRepo:
    def __init__(self, *bovines: Bovine) -> None:
        self.rows = {b.id: b for b in bovines}
        self.events: list[str] = []

    def get_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine | None:
        b = self.rows.get(bovine_id)
        return b if b is not None and b.farm_id == farm_id else None

    def get_active_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine | None:
        b = self.get_in_farm(farm_id, bovine_id)
        return b if b is not None and b.is_active else None

    def identification_taken(self, farm_id: uuid.UUID, ident: str, *, exclude_id: uuid.UUID | None = None) -> bool:
        return any(b.farm_id == farm_id and b.identification_number == ident and b.id != exclude_id
                   for b in self.rows.values())

    def add(self, row: Any) -> None:
        row.id = row.id or uuid.uuid4()
        self.rows[row.id] = row
        self.events.append("add")

    def flush(self) -> None:
        self.events.append("flush")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")

    def refresh(self, row: Any) -> None:
        self.events.append("refresh")


def _bovine_service(*bovines: Bovine, paddock: PaddockRef | None = None, names: dict[str, uuid.UUID] | None = None) -> tuple[BovineService, FakeBovineRepo, MagicMock, MagicMock]:
    repo, scope, audit = FakeBovineRepo(*bovines), MagicMock(), MagicMock()
    names = names or {}
    service = BovineService(
        repo,  # type: ignore[arg-type]
        land_plot_exists=lambda farm_id, plot_id: plot_id in (PLOT, OTHER_PLOT),
        find_paddock=lambda farm_id, paddock_id: paddock if paddock and paddock.id == paddock_id else None,
        ensure_farm_scope=scope,
        land_plot_id_by_name=lambda farm_id, name: names.get(f"lote:{name.strip().lower()}"),  # como el real: sin mayúsculas
        paddock_id_by_name=lambda farm_id, name: names.get(f"potrero:{name.strip().lower()}"),
        record_audit=audit,
    )
    return service, repo, scope, audit


def _create(**overrides: Any) -> BovineCreate:
    values: dict[str, Any] = {"identification_number": "BT-9", "sex": "macho", "birth_date": date(2026, 1, 1),
                              "entry_type": "compra", "entry_date": date(2026, 2, 1)}
    values.update(overrides)
    return BovineCreate(**values)


@pytest.mark.parametrize(
    ("overrides", "error", "message"),
    [
        ({"identification_number": "BT-1"}, ConflictError, bovines_mod.DUPLICATE_IDENTIFICATION),
        ({"mother_id": uuid.uuid4()}, BusinessRuleError, bovines_mod.PARENT_NOT_IN_FARM),
        ({"land_plot_id": uuid.uuid4()}, BusinessRuleError, bovines_mod.PLOT_NOT_IN_FARM),
        ({"paddock_id": uuid.uuid4()}, BusinessRuleError, bovines_mod.PADDOCK_NOT_IN_FARM),
        ({"paddock_id": PADDOCK, "land_plot_id": OTHER_PLOT}, BusinessRuleError, bovines_mod.PADDOCK_OTHER_PLOT),
    ],
)
def test_bovine_create_rules(overrides: dict[str, Any], error: type, message: str) -> None:
    service, repo, _, _ = _bovine_service(_bovine(), paddock=PaddockRef(PADDOCK, PLOT))

    with pytest.raises(error) as exc:
        service.create_bovine(FARM, _create(**overrides), USER)
    assert exc.value.message == message
    assert "add" not in repo.events


def test_bovine_create_takes_land_plot_from_paddock_and_audits_in_same_transaction() -> None:
    service, repo, _, audit = _bovine_service(paddock=PaddockRef(PADDOCK, PLOT))

    bovine = service.create_bovine(FARM, _create(paddock_id=PADDOCK), USER)

    assert bovine.land_plot_id == PLOT
    assert repo.events == ["add", "flush", "commit", "refresh"]
    assert audit.call_args.kwargs["details"] == {"tag": "BT-9"}


def test_bovine_update_identification_must_stay_unique_except_itself() -> None:
    a, b = _bovine(identification_number="A"), _bovine(identification_number="B")
    service, _, _, _ = _bovine_service(a, b)

    service.update_bovine(FARM, a.id, BovineUpdate(identification_number="A"), USER)  # el suyo: OK
    with pytest.raises(ConflictError):
        service.update_bovine(FARM, a.id, BovineUpdate(identification_number="B"), USER)


def test_bovine_delete_is_logical() -> None:
    cow = _bovine()
    service, _, _, _ = _bovine_service(cow)

    service.delete_bovine(FARM, cow.id, USER)

    assert (cow.is_active, cow.status, cow.exit_reason) == (False, "retirado", "retirado")
    assert cow.exit_date is not None


def test_bovine_csv_import_resolves_names_and_reports_rows() -> None:
    service, repo, _, _ = _bovine_service(_bovine(identification_number="DUP"), paddock=PaddockRef(PADDOCK, PLOT),
                                          names={"lote:norte": PLOT, "potrero:p1": PADDOCK})
    csv_text = (
        "identification_number,sex,birth_date,entry_type,entry_date,lote,potrero,birth_weight\n"
        "N-1,Hembra,2026-01-01,compra,2026-02-01,Norte,P1,\"32,5\"\n"   # válida (nombres y coma decimal)
        "N-2,otro,2026-01-01,compra,2026-02-01,,,\n"                   # sexo inválido
        "DUP,macho,2026-01-01,compra,2026-02-01,,,\n"                  # identificación repetida
    )

    result = service.import_csv(FARM, csv_text, USER)

    assert (result["total"], result["imported"], result["failed"]) == (3, 1, 2)
    created = next(b for b in repo.rows.values() if b.identification_number == "N-1")
    assert (created.land_plot_id, created.paddock_id, created.birth_weight) == (PLOT, PADDOCK, Decimal("32.5"))
    rows = [(e["row"], e["error"]) for e in result["errors"]]
    assert rows[0][0] == 3 and "El sexo debe ser" in rows[0][1]
    # Número de línea REAL del CSV (antes se informaba 3: se contaban solo filas válidas).
    assert rows[1] == (4, bovines_mod.DUPLICATE_IDENTIFICATION)


def test_bovine_csv_without_headers_is_rejected() -> None:
    service, _, _, _ = _bovine_service()

    with pytest.raises(BusinessRuleError) as exc:
        service.import_csv(FARM, "", USER)
    assert exc.value.message == bovines_mod.CSV_WITHOUT_HEADERS


def test_calf_registration_flushes_but_does_not_commit() -> None:
    service, repo, _, audit = _bovine_service()

    calf_id = service.register_calf_from_birth(FARM, identification_number="CRIA-1", sex="macho",
                                               birth_date=TODAY, mother_id=uuid.uuid4(), registered_by=USER)

    assert repo.events == ["add", "flush"]  # el commit lo hace el evento reproductivo
    assert repo.rows[calf_id].entry_type == "nacimiento"
    assert audit.call_args.kwargs["details"]["calf_from"] == "parto"


# ═══════════════════════════════════════════════════════════════
# Pesajes
# ═══════════════════════════════════════════════════════════════


def test_daily_gain_formula() -> None:
    previous = Weight(weight_kg=Decimal("100"), measured_at=date(2026, 11, 1))

    assert daily_gain(Decimal("110"), date(2026, 11, 11), previous) == Decimal("1.00")
    assert daily_gain(Decimal("110"), date(2026, 11, 1), previous) is None  # mismo día
    assert daily_gain(Decimal("110"), date(2026, 11, 11), None) is None     # primer pesaje


@pytest.mark.parametrize(("latest", "updates"), [(None, True), (date(2026, 11, 1), True), (date(2026, 12, 1), False)])
def test_weight_only_updates_current_weight_when_it_is_the_latest(latest: date | None, updates: bool) -> None:
    cow = _bovine(current_weight=Decimal("200"))
    bovines, weights = MagicMock(), MagicMock()
    bovines.get_active_in_farm.return_value = cow
    weights.previous_before.return_value = None
    weights.latest_measured_at.return_value = latest
    service = WeightService(weights, bovines, MagicMock())

    service.create_weight(FARM, cow.id, WeightCreate(weight_kg=Decimal("250"), measured_at=date(2026, 11, 20)), USER)

    assert cow.current_weight == (Decimal("250") if updates else Decimal("200"))


def test_weight_of_inactive_bovine_is_404() -> None:
    bovines = MagicMock()
    bovines.get_active_in_farm.return_value = None
    service = WeightService(MagicMock(), bovines, MagicMock())

    with pytest.raises(NotFoundError) as exc:
        service.list_weights(FARM, uuid.uuid4())
    assert exc.value.message == "Bovino no encontrado en esta finca."


# ═══════════════════════════════════════════════════════════════
# Terneros
# ═══════════════════════════════════════════════════════════════


def _calves(*bovines: Bovine) -> tuple[CalfService, MagicMock, MagicMock]:
    repo_b, repo_w = MagicMock(), MagicMock()
    by_id = {b.id: b for b in bovines}
    repo_b.get_active_in_farm.side_effect = lambda farm_id, bid: by_id.get(bid)
    repo_w.exists_on_date.return_value = False
    repo_w.previous_before.return_value = None
    repo_w.latest_measured_at.return_value = None
    return CalfService(repo_b, repo_w, MagicMock(), today=lambda: TODAY), repo_b, repo_w


def test_calf_growth_metrics_against_breed_table() -> None:
    calf = _bovine(birth_date=TODAY - timedelta(days=30), breed="angus", birth_weight=Decimal("35"),
                   current_weight=Decimal("50"))

    metrics = calves_mod.calculate_growth_metrics(calf, TODAY)

    assert metrics.days_old == 30
    assert metrics.expected_weight_kg == Decimal("50")       # Angus a los 30 días
    assert metrics.growth_percentage == Decimal("100")
    assert metrics.daily_gain_kg == Decimal("0.5")           # (50 - 35) / 30
    assert metrics.feeding_plan.startswith("Leche materna + introducir concentrado")


def test_calf_older_than_a_year_is_not_a_calf() -> None:
    old = _bovine(birth_date=TODAY - timedelta(days=400))
    service, _, _ = _calves(old)

    with pytest.raises(BusinessRuleError) as exc:
        service.get_calf_details(FARM, old.id)
    assert exc.value.message == calves_mod.NOT_A_CALF_ANYMORE


def test_calf_list_uses_age_window() -> None:
    service, repo_b, _ = _calves()

    service.list_calves(FARM, max_age_days=90, min_age_days=30, status_filter="activo")

    repo_b.list_active_born_between.assert_called_once_with(
        FARM, born_after=TODAY - timedelta(days=90), born_on_or_before=TODAY - timedelta(days=30), status="activo",
    )


@pytest.mark.parametrize(
    ("measured", "exists", "message"),
    [(date(2026, 5, 1), False, calves_mod.MEASURED_BEFORE_BIRTH), (TODAY, True, calves_mod.WEIGHT_ALREADY_ON_DATE)],
)
def test_calf_weight_rules(measured: date, exists: bool, message: str) -> None:
    calf = _bovine(birth_date=date(2026, 6, 1))
    service, _, repo_w = _calves(calf)
    repo_w.exists_on_date.return_value = exists

    with pytest.raises(BusinessRuleError) as exc:
        service.record_calf_weight(FARM, calf.id, Decimal("60"), measured, user_id=USER)
    assert exc.value.message == message


def test_calf_summary_buckets() -> None:
    service, repo_b, repo_w = _calves()
    repo_b.count_active_born.side_effect = lambda farm_id, after, before=None: {
        (TODAY - timedelta(days=365), None): 10, (TODAY - timedelta(days=30), None): 3,
        (TODAY - timedelta(days=90), TODAY - timedelta(days=30)): 4,
        (TODAY - timedelta(days=365), TODAY - timedelta(days=90)): 3,
    }[(after, before)]
    repo_b.avg_current_weight_born_after.return_value = Decimal("80.5")
    repo_w.avg_daily_gain_of_calves.return_value = None

    summary = service.get_calf_summary_by_farm(FARM)

    assert summary == {"total_calves": 10, "calves_0_30_days": 3, "calves_31_90_days": 4,
                       "calves_91_365_days": 3, "average_weight_kg": 80.5, "average_daily_gain": 0}


# ═══════════════════════════════════════════════════════════════
# Movimientos
# ═══════════════════════════════════════════════════════════════


def _movements(*bovines: Bovine, duplicate: bool = False) -> MovementService:
    repo_m, repo_b = MagicMock(), MagicMock()
    by_id = {b.id: b for b in bovines}
    repo_b.get_in_farm.side_effect = lambda farm_id, bid: by_id.get(bid)
    repo_m.duplicate_exists.return_value = duplicate
    return MovementService(repo_m, repo_b, MagicMock())


@pytest.mark.parametrize(
    ("movement_type", "status", "active", "exit_reason"),
    [("venta", "vendido", False, "venta"), ("muerte", "muerto", False, "muerte"), ("traslado", "activo", True, None)],
)
def test_movement_updates_bovine_status(movement_type: str, status: str, active: bool, exit_reason: str | None) -> None:
    cow = _bovine()
    service = _movements(cow)

    service.create_movement(FARM, MovementCreate(bovine_id=cow.id, movement_type=movement_type,
                                                 movement_date=date(2026, 11, 1)), USER)

    assert (cow.status, cow.is_active, cow.exit_reason) == (status, active, exit_reason)


def test_movement_rules() -> None:
    cow = _bovine()
    data = MovementCreate(bovine_id=cow.id, movement_type="venta", movement_date=date(2026, 11, 1))

    with pytest.raises(BusinessRuleError) as dup:
        _movements(cow, duplicate=True).create_movement(FARM, data, USER)
    with pytest.raises(NotFoundError) as missing:
        _movements().create_movement(FARM, data, USER)
    assert dup.value.message == movements_mod.DUPLICATE_MOVEMENT
    assert missing.value.message == movements_mod.BOVINE_NOT_IN_FARM


def test_movements_are_immutable() -> None:
    service = _movements()

    with pytest.raises(PermissionDeniedError) as upd:
        service.update_movement(FARM, uuid.uuid4())
    with pytest.raises(PermissionDeniedError) as dele:
        service.delete_movement(FARM, uuid.uuid4())
    assert upd.value.message == movements_mod.IMMUTABLE_UPDATE
    assert dele.value.message == movements_mod.IMMUTABLE_DELETE


# ═══════════════════════════════════════════════════════════════
# Plan de alimentación (ahora en inventory)
# ═══════════════════════════════════════════════════════════════


def test_feeding_plan_lives_in_inventory_and_validates() -> None:
    from app.modules.inventory.models import Food
    from app.modules.inventory.service import CALF_NOT_FOUND, FOOD_NOT_FOUND, QUANTITY_NOT_POSITIVE, CalfFeedingService

    calf_id, food = uuid.uuid4(), Food(id=uuid.uuid4(), farm_id=FARM, name="Concentrado")
    repo = MagicMock()
    repo.get_food_in_farm.side_effect = lambda farm_id, food_id: food if food_id == food.id else None
    service = CalfFeedingService(repo, lambda farm_id, bid: BovineRef(bid, "macho") if bid == calf_id else None)

    plan = service.update_calf_feeding_plan(FARM, calf_id, food.id, Decimal("2.5"), TODAY)
    assert plan["food_name"] == "Concentrado" and plan["start_date"] == "2026-11-20"

    for args, message in [((uuid.uuid4(), food.id, Decimal("1")), CALF_NOT_FOUND),
                          ((calf_id, uuid.uuid4(), Decimal("1")), FOOD_NOT_FOUND),
                          ((calf_id, food.id, Decimal("0")), QUANTITY_NOT_POSITIVE)]:
        with pytest.raises((NotFoundError, BusinessRuleError)) as exc:
            service.update_calf_feeding_plan(FARM, *args, TODAY)
        assert exc.value.message == message


# ═══════════════════════════════════════════════════════════════
# Repositorios y puertos ofrecidos (tablas reales en SQLite)
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def db() -> Iterator[Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite://")
    for table in (Bovine.__table__, Weight.__table__, AnimalMovement.__table__):
        table.create(engine)
    with Session(engine) as session:
        yield session


def test_repository_calf_queries(db: Any) -> None:
    from app.modules.livestock.repository import BovineRepository

    for days, active in ((10, True), (60, True), (200, True), (400, True), (20, False)):
        db.add(_bovine(identification_number=f"B{days}{active}", birth_date=TODAY - timedelta(days=days), is_active=active))
    db.commit()
    repo = BovineRepository(db)

    young = repo.list_active_born_between(FARM, TODAY - timedelta(days=365), TODAY)
    assert [(TODAY - b.birth_date).days for b in young] == [10, 60, 200]  # los más jóvenes primero, sin inactivos
    assert repo.count_active_born(FARM, TODAY - timedelta(days=90), TODAY - timedelta(days=30)) == 1
    assert repo.identification_taken(FARM, "B10True") is True
    assert repo.list_breeds(FARM) == []


def test_repository_weight_queries(db: Any) -> None:
    from app.modules.livestock.repository import WeightRepository

    cow = _bovine()
    db.add(cow)
    for day, kg in ((1, "100"), (11, "110")):
        db.add(Weight(farm_id=FARM, bovine_id=cow.id, weight_kg=Decimal(kg), measured_at=date(2026, 11, day), registered_by=USER))
    db.commit()
    repo = WeightRepository(db)

    assert repo.previous_before(cow.id, date(2026, 11, 11)).weight_kg == Decimal("100")
    assert repo.latest_measured_at(cow.id) == date(2026, 11, 11)
    assert repo.exists_on_date(cow.id, date(2026, 11, 1)) is True
    assert [w.weight_kg for w in repo.list_for_bovine(FARM, cow.id, since=date(2026, 11, 5))] == [Decimal("110")]


def test_provided_bovine_lookup_returns_ref_not_orm(db: Any) -> None:
    from app.modules import livestock

    cow = _bovine(sex="hembra")
    db.add(cow)
    db.commit()
    lookup = livestock.build_bovine_lookup(db)

    assert lookup(FARM, cow.id) == BovineRef(cow.id, "hembra")
    assert lookup(uuid.uuid4(), cow.id) is None  # otra finca


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
def client() -> Iterator[tuple[TestClient, Any]]:
    from app.core.database import get_db
    from app.core.limiter import limiter
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.livestock.dependencies import get_bovine_service, get_movement_service

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = _AllowAllSession
    app.dependency_overrides[get_bovine_service] = lambda: _bovine_service(_bovine())[0]
    app.dependency_overrides[get_movement_service] = lambda: _movements()
    was_enabled, limiter.enabled = limiter.enabled, False
    try:
        yield TestClient(app), app
    finally:
        limiter.enabled = was_enabled
        app.dependency_overrides.clear()


def test_http_duplicate_bovine_is_409(client: tuple[TestClient, Any]) -> None:
    http, _ = client
    response = http.post(f"/api/v1/farms/{FARM}/bovines", json={
        "identification_number": "BT-1", "sex": "hembra", "birth_date": "2026-01-01",
        "entry_type": "compra", "entry_date": "2026-02-01",
    })

    assert (response.status_code, response.json()) == (409, {"detail": bovines_mod.DUPLICATE_IDENTIFICATION})


def test_http_csv_import_goes_through_the_service(client: tuple[TestClient, Any]) -> None:
    http, _ = client
    csv_bytes = "identification_number,sex,birth_date,entry_type,entry_date\nX-1,macho,2026-01-01,compra,2026-02-01\n".encode("utf-8-sig")

    response = http.post(f"/api/v1/farms/{FARM}/bovines/import", files={"file": ("hato.csv", csv_bytes, "text/csv")})

    assert response.status_code == 200
    assert response.json() == {"total": 1, "imported": 1, "failed": 0, "errors": []}


def test_http_movements_are_immutable(client: tuple[TestClient, Any]) -> None:
    http, _ = client
    url = f"/api/v1/farms/{FARM}/movements/{uuid.uuid4()}"

    put = http.put(url, json={"observations": "corrección"})
    delete = http.delete(url)

    assert (put.status_code, put.json()) == (403, {"detail": movements_mod.IMMUTABLE_UPDATE})
    assert (delete.status_code, delete.json()) == (403, {"detail": movements_mod.IMMUTABLE_DELETE})


def test_http_all_livestock_routes_and_feeding_plan_are_mounted(client: tuple[TestClient, Any]) -> None:
    _, app = client
    routes = {(r.path, tuple(r.tags)) for r in app.routes if hasattr(r, "tags")}  # type: ignore[attr-defined]

    for path in ("/api/v1/farms/{farm_id}/bovines", "/api/v1/farms/{farm_id}/bovines/{bovine_id}/weights",
                 "/api/v1/farms/{farm_id}/calves/summary", "/api/v1/farms/{farm_id}/movements"):
        assert any(p == path for p, _ in routes), path
    assert ("/api/v1/farms/{farm_id}/calves/{bovine_id}/feeding-plan", ("Terneros (HU007)",)) in routes


@pytest.mark.parametrize("entrypoint", ["app.modules.livestock", "app.modules.inventory"])
def test_module_boots_like_uvicorn(entrypoint: str) -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", f"import {entrypoint}; import app.main"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr[-1500:]
