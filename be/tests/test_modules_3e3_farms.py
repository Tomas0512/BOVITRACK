"""
Pruebas de la Parte 3e-3 del refactor: módulo farms.

  - FarmService (fakes): identificador y nombre únicos, membresía del creador vía
    identity en la misma transacción, quién puede ver una finca.
  - Lotes y potreros contra tablas reales (SQLite): reglas de rotación, los
    animales de cada potrero (modelo de lectura sobre `bovine`) y los bugs
    corregidos #17, #18 y #19.
  - FarmScopeService y los puertos que farms ofrece a otros módulos.
  - Frontera: farms solo carga a identity; sus rutas las sirve el módulo.
"""

import uuid
from collections.abc import Iterator
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todas las tablas
from app.modules.farms.models import Farm, Paddock
from app.modules.farms.schemas import FarmCreate, FarmUpdate, LandPlotCreate, PaddockCreate, PaddockUpdate
from app.modules.farms.service import FarmScopeService, FarmService, LandPlotService, PaddockService
from app.modules.farms.service import farms as farm_rules
from app.modules.farms.service import land_plots as land_plot_rules
from app.modules.farms.service import paddocks as paddock_rules
from app.modules.farms.service import scope as scope_rules
from app.shared.exceptions import (
    BusinessRuleError,
    ConflictError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
)

OWNER, MEMBER, STRANGER = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
DEPT = uuid.uuid4()


def _farm_data(**overrides: Any) -> FarmCreate:
    data: dict[str, Any] = {
        "name": "La Esperanza", "address": "Vereda El Carmen", "department_id": DEPT, "city_municipality": "Montería",
        "total_area": Decimal("50"), "purpose_id": uuid.uuid4(), "farm_identifier": "F-001",
    }
    data.update(overrides)
    return FarmCreate(**data)


# ═══════════════════════════════════════════════════════════════
# FarmService (fakes)
# ═══════════════════════════════════════════════════════════════


class FakeFarms:
    def __init__(self, *farms: Farm) -> None:
        self.farms = list(farms)
        self.log: list[str] = []

    def get_active(self, farm_id: uuid.UUID) -> Farm | None:
        return next((f for f in self.farms if f.id == farm_id and f.is_active), None)

    def by_identifier(self, identifier: str, *, exclude_id: uuid.UUID | None = None) -> Farm | None:
        return next((f for f in self.farms if f.farm_identifier == identifier and f.id != exclude_id), None)

    def by_location(self, name: str, department_id: uuid.UUID, city: str, *, exclude_id: uuid.UUID | None = None) -> Farm | None:
        return next((f for f in self.farms if (f.name, f.department_id, f.city_municipality) == (name, department_id, city)
                     and f.id != exclude_id), None)

    def list_visible(self, user_id: uuid.UUID, member_farm_ids: list[uuid.UUID]) -> list[Farm]:
        return [f for f in self.farms if f.is_active and (f.owner_id == user_id or f.id in member_farm_ids)]

    def add(self, farm: Farm) -> None:
        self.log.append("add")
        self.farms.append(farm)

    def flush(self) -> None:
        self.log.append("flush")
        for farm in self.farms:
            farm.id = farm.id or uuid.uuid4()
            farm.is_active = True if farm.is_active is None else farm.is_active

    def commit(self) -> None:
        self.log.append("commit")

    def rollback(self) -> None:
        self.log.append("rollback")

    def refresh(self, farm: Farm) -> None:  # como la BD: completa las fechas y valores por defecto
        now = datetime.now(timezone.utc)
        farm.created_at, farm.updated_at = farm.created_at or now, farm.updated_at or now
        farm.area_unit = farm.area_unit or "hectareas"


def _farm_service(repo: FakeFarms, members: dict[uuid.UUID, list[uuid.UUID]] | None = None) -> tuple[FarmService, list]:
    members = members or {}
    events: list = []
    service = FarmService(
        repo,
        grant_admin=lambda user_id, farm_id: (repo.log.append("grant"), events.append(("admin", user_id, farm_id))),
        member_farm_ids=lambda user_id: [f for f, users in members.items() if user_id in users],
        is_member=lambda farm_id, user_id: user_id in members.get(farm_id, []),
        record_audit=lambda **kw: (repo.log.append("audit"), events.append(kw)),
    )
    return service, events


def _existing_farm(**overrides: Any) -> Farm:
    data: dict[str, Any] = {"id": uuid.uuid4(), "owner_id": OWNER, "name": "La Esperanza", "address": "x",
                            "department_id": DEPT, "city_municipality": "Montería", "total_area": 1,
                            "purpose_id": uuid.uuid4(), "farm_identifier": "F-001", "is_active": True}
    data.update(overrides)
    return Farm(**data)


def test_create_farm_grants_admin_in_the_same_transaction() -> None:
    repo = FakeFarms()
    service, events = _farm_service(repo)

    farm = service.create(_farm_data(), OWNER)

    assert repo.log == ["add", "flush", "grant", "audit", "commit"]  # una sola transacción
    assert events[0] == ("admin", OWNER, farm.id)
    assert events[1]["action"] == "create" and events[1]["details"] == {"name": "La Esperanza"}


def test_create_farm_rejects_duplicates() -> None:
    service, _ = _farm_service(FakeFarms(_existing_farm()))

    with pytest.raises(ConflictError) as exc:
        service.create(_farm_data(name="Otra"), OWNER)
    assert exc.value.message == farm_rules.FARM_IDENTIFIER_TAKEN
    # Bug #19: mismo nombre en el mismo municipio -> antes 500 (choque con uq_farm_name_location)
    with pytest.raises(ConflictError) as exc:
        service.create(_farm_data(farm_identifier="F-002"), OWNER)
    assert exc.value.message == farm_rules.FARM_NAME_TAKEN
    service.create(_farm_data(farm_identifier="F-003", city_municipality="Cereté"), OWNER)  # otro municipio: vale


def test_bulk_create_reports_each_row_and_keeps_going() -> None:
    """Carga masiva con reporte por fila: una finca con error no impide crear las demás."""
    repo = FakeFarms(_existing_farm(farm_identifier="F-EXISTE"))
    service, _ = _farm_service(repo)
    items = [
        _farm_data(name="Uno", farm_identifier="F-1"),
        _farm_data(name="Dos", farm_identifier="F-EXISTE"),  # ya existe en la BD
        _farm_data(name="Tres", farm_identifier="F-3"),
        _farm_data(name="Cuatro", farm_identifier="F-1"),  # repetida DENTRO de la lista
        _farm_data(name="Uno", farm_identifier="F-5"),  # mismo nombre y municipio que la fila 1
    ]

    result = service.create_many(items, OWNER)

    assert (result.total, result.created, result.failed) == (5, 2, 3)
    assert [f.name for f in result.items] == ["Uno", "Tres"]
    assert [(e.row, e.farm_identifier, e.error) for e in result.errors] == [
        (2, "F-EXISTE", farm_rules.FARM_IDENTIFIER_TAKEN),
        (4, "F-1", farm_rules.FARM_IDENTIFIER_TAKEN),
        (5, "F-5", farm_rules.FARM_NAME_TAKEN),
    ]
    assert repo.log.count("commit") == 2  # cada finca creada es su propia transacción


def test_bulk_create_unexpected_error_rolls_back_only_that_row() -> None:
    repo = FakeFarms()
    calls = {"n": 0}

    def flaky_grant(user_id: uuid.UUID, farm_id: uuid.UUID) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("se cayó la conexión")

    service = FarmService(repo, grant_admin=flaky_grant, member_farm_ids=lambda u: [], is_member=lambda f, u: False,
                          record_audit=lambda **kw: None)

    result = service.create_many([_farm_data(farm_identifier=f"F-{i}", name=f"N{i}") for i in range(3)], OWNER)

    assert (result.created, result.failed) == (2, 1)
    assert (result.errors[0].row, result.errors[0].error) == (2, farm_rules.UNEXPECTED_ROW_ERROR)
    assert "rollback" in repo.log


def test_who_can_see_a_farm() -> None:
    farm = _existing_farm()
    service, _ = _farm_service(FakeFarms(farm), members={farm.id: [MEMBER]})

    assert service.get_for_user(farm.id, OWNER) is farm
    assert service.get_for_user(farm.id, MEMBER) is farm
    with pytest.raises(PermissionDeniedError) as exc:
        service.get_for_user(farm.id, STRANGER)
    assert exc.value.message == farm_rules.NO_FARM_ACCESS
    with pytest.raises(NotFoundError):
        service.get_for_user(uuid.uuid4(), OWNER)
    assert service.list_for_user(MEMBER) == [farm] and service.list_for_user(STRANGER) == []


def test_update_and_deactivate_farm() -> None:
    farm, other = _existing_farm(), _existing_farm(name="Vecina", farm_identifier="F-009")
    repo = FakeFarms(farm, other)
    service, events = _farm_service(repo)

    with pytest.raises(ConflictError):
        service.update(farm.id, OWNER, FarmUpdate(farm_identifier="F-009"))
    with pytest.raises(ConflictError) as exc:
        service.update(farm.id, OWNER, FarmUpdate(name="Vecina"))
    assert exc.value.message == farm_rules.FARM_NAME_TAKEN
    assert service.update(farm.id, OWNER, FarmUpdate(phone="300")).phone == "300"  # sin tocar nombre: no choca consigo

    service.deactivate(farm.id, OWNER)
    assert farm.is_active is False and events[-1]["action"] == "delete"
    with pytest.raises(NotFoundError):
        service.get_for_user(farm.id, OWNER)


# ═══════════════════════════════════════════════════════════════
# Tablas reales (SQLite): lotes, potreros, puertos
# ═══════════════════════════════════════════════════════════════

FARM, OTHER_FARM = uuid.uuid4(), uuid.uuid4()


def _fill_required(table: Any, values: dict[str, Any]) -> dict[str, Any]:
    """Completa las columnas obligatorias que la prueba no menciona (SQLite no valida FKs)."""
    from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, Uuid

    row = dict(values)
    for col in table.columns:
        if col.name in row or col.nullable or col.default is not None or col.server_default is not None:
            continue
        kind = col.type
        row[col.name] = (
            uuid.uuid4() if isinstance(kind, Uuid) else
            True if isinstance(kind, Boolean) else
            datetime(2026, 1, 1, tzinfo=timezone.utc) if isinstance(kind, DateTime) else
            date(2026, 1, 1) if isinstance(kind, Date) else
            1 if isinstance(kind, Integer | Numeric) else "x"
        )
    return row


@pytest.fixture
def db() -> Iterator[Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base
    from app.modules.identity.models import Role, UserFarm

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for name in ("users", "role", "farm", "user_farm", "land_plot", "paddock", "bovine", "department", "city", "purpose"):
        Base.metadata.tables[name].create(engine)
    with Session(engine) as session:
        for fid in (FARM, OTHER_FARM):
            session.execute(Base.metadata.tables["farm"].insert(), [_fill_required(
                Base.metadata.tables["farm"], {"id": fid, "owner_id": OWNER, "name": str(fid), "farm_identifier": str(fid),
                                               "is_active": True, "area_unit": "hectareas"})])
        admin = Role(name="Administrador")
        session.add(admin)
        session.flush()
        session.add(UserFarm(user_id=MEMBER, farm_id=FARM, role_id=admin.id))
        session.commit()
        yield session


def _land_plot_data(name: str = "Lote Norte", paddocks: tuple[str, ...] = ("P1", "P2")) -> LandPlotCreate:
    return LandPlotCreate(name=name, area=Decimal("20"), usage_type="pastoreo", max_capacity=40,
                          paddocks=[{"name": p, "area_hectares": Decimal("5"), "max_capacity": 10} for p in paddocks])


def _services(db: Any) -> tuple[LandPlotService, PaddockService, list[dict]]:
    from app.modules.farms.repository import LandPlotRepository, PaddockRepository

    audits: list[dict] = []
    record = lambda **kw: audits.append(kw)  # noqa: E731
    return (LandPlotService(LandPlotRepository(db), PaddockRepository(db), record_audit=record),
            PaddockService(PaddockRepository(db), LandPlotRepository(db), record_audit=record), audits)


def test_land_plot_is_created_with_its_paddocks_and_unique_names(db: Any) -> None:
    land_plots, paddocks, audits = _services(db)

    lp = land_plots.create(FARM, _land_plot_data(), OWNER)

    assert sorted(p.name for p in paddocks.list(FARM)) == ["P1", "P2"]
    assert audits[-1]["details"] == {"name": "Lote Norte", "paddocks": ["P1", "P2"]}
    with pytest.raises(ConflictError) as exc:
        land_plots.create(FARM, _land_plot_data(paddocks=("P9",)), OWNER)
    assert exc.value.message == land_plot_rules.LAND_PLOT_NAME_TAKEN
    with pytest.raises(ConflictError) as exc:  # potrero repetido en la finca: nada se escribe
        land_plots.create(FARM, _land_plot_data("Lote Sur", ("P2",)), OWNER)
    assert exc.value.message == "Ya existe un potrero llamado 'P2' en esta finca"
    assert [x.name for x in land_plots.list(FARM)] == ["Lote Norte"]
    land_plots.create(OTHER_FARM, _land_plot_data(), OWNER)  # otra finca: los nombres no chocan
    assert land_plots.get(FARM, lp.id) is lp


def test_bugfix_17_deactivating_a_land_plot_deactivates_its_paddocks(db: Any) -> None:
    """Regresión #17: antes `lp.paddocks` no existía en el modelo y DELETE de un lote daba 500."""
    land_plots, paddocks, _ = _services(db)
    lp = land_plots.create(FARM, _land_plot_data(), OWNER)

    land_plots.deactivate(FARM, lp.id, OWNER)

    assert lp.is_active is False
    assert paddocks.list(FARM) == []  # sus potreros quedaron inactivos
    assert all(p.is_active is False for p in db.query(Paddock).filter_by(land_plot_id=lp.id))


def test_paddock_rules(db: Any) -> None:
    land_plots, paddocks, _ = _services(db)
    lp = land_plots.create(FARM, _land_plot_data(), OWNER)

    def data(**kw: Any) -> PaddockCreate:
        base: dict[str, Any] = {"land_plot_id": lp.id, "name": "P3", "area_hectares": Decimal("5"), "max_capacity": 10}
        base.update(kw)
        return PaddockCreate(**base)

    with pytest.raises(InvalidRequestError) as exc:
        paddocks.create(OTHER_FARM, data(), OWNER)  # el lote es de otra finca
    assert exc.value.message == paddock_rules.LAND_PLOT_UNUSABLE
    with pytest.raises(InvalidRequestError) as exc:
        paddocks.create(FARM, data(max_capacity=41), OWNER)
    assert exc.value.message == "La capacidad del potrero no puede superar la del lote (40)."
    with pytest.raises(InvalidRequestError):
        paddocks.create(FARM, data(area_hectares=Decimal("21")), OWNER)

    p3 = paddocks.create(FARM, data(), OWNER)
    assert p3.land_plot_name == "Lote Norte"
    with pytest.raises(NotFoundError):
        paddocks.get(OTHER_FARM, p3.id)


def test_bugfix_18_duplicate_paddock_name_is_409_not_500(db: Any) -> None:
    """Regresión #18: un nombre repetido chocaba con uq_paddock_farm_name y daba 500."""
    land_plots, paddocks, _ = _services(db)
    lp = land_plots.create(FARM, _land_plot_data(), OWNER)
    p1 = next(p for p in paddocks.list(FARM) if p.name == "P1")

    with pytest.raises(ConflictError) as exc:
        paddocks.create(FARM, PaddockCreate(land_plot_id=lp.id, name="P2", area_hectares=Decimal("1"), max_capacity=1), OWNER)
    assert exc.value.message == "Ya existe un potrero llamado 'P2' en esta finca"
    with pytest.raises(ConflictError):
        paddocks.update(FARM, p1.id, PaddockUpdate(name="P2"), OWNER)
    assert paddocks.update(FARM, p1.id, PaddockUpdate(name="P1", status="ocupado"), OWNER).status == "ocupado"


def test_last_paddock_of_a_land_plot_cannot_be_deactivated(db: Any) -> None:
    land_plots, paddocks, _ = _services(db)
    land_plots.create(FARM, _land_plot_data(paddocks=("Único", "Otro")), OWNER)
    first, second = paddocks.list(FARM)

    paddocks.deactivate(FARM, first.id, OWNER)
    with pytest.raises(BusinessRuleError) as exc:
        paddocks.deactivate(FARM, second.id, OWNER)
    assert exc.value.message == paddock_rules.LAST_PADDOCK


def test_paddock_responses_include_their_active_animals(db: Any) -> None:
    from app.core.database import Base

    land_plots, paddocks, _ = _services(db)
    land_plots.create(FARM, _land_plot_data(), OWNER)
    p1, p2 = paddocks.list(FARM)
    bovine = Base.metadata.tables["bovine"]
    for number, paddock_id, active in (("B-2", p1.id, True), ("B-1", p1.id, True), ("B-3", p1.id, False), ("B-4", p2.id, True)):
        db.execute(bovine.insert(), [_fill_required(bovine, {"farm_id": FARM, "paddock_id": paddock_id, "is_active": active,
                                                             "identification_number": number, "name": None})])

    first, second = paddocks.with_animals([p1, p2])

    assert [a.identification_number for a in first.animals] == ["B-1", "B-2"]  # sin el inactivo, ordenados
    assert (first.animal_count, second.animal_count) == (2, 1)
    assert paddocks.with_animals([]) == []


def test_ports_offered_to_other_modules(db: Any) -> None:
    from app.modules import farms

    land_plots, paddocks, _ = _services(db)
    lp = land_plots.create(FARM, _land_plot_data(), OWNER)
    p1 = next(p for p in paddocks.list(FARM) if p.name == "P1")

    assert farms.build_land_plot_lookup(db)(FARM, lp.id) and not farms.build_land_plot_lookup(db)(OTHER_FARM, lp.id)
    ref = farms.build_paddock_lookup(db)(FARM, p1.id)
    assert (ref.id, ref.land_plot_id) == (p1.id, lp.id)
    assert farms.build_land_plot_id_by_name(db)(FARM, "  lote NORTE ") == lp.id
    assert farms.build_paddock_id_by_name(db)(FARM, "p1") == p1.id
    assert farms.build_paddock_id_by_name(db)(OTHER_FARM, "p1") is None
    assert sorted(farms.list_active_farm_ids(db)) == sorted([FARM, OTHER_FARM])

    p1.is_active = False
    db.commit()
    assert farms.build_paddock_lookup(db)(FARM, p1.id) is None  # solo potreros activos


# ═══════════════════════════════════════════════════════════════
# Alcance de finca
# ═══════════════════════════════════════════════════════════════


def test_farm_scope_rules() -> None:
    bovine_in_farm = uuid.uuid4()
    check = FarmScopeService(
        land_plot_exists=lambda farm_id, land_plot_id: land_plot_id == FARM,
        farm_owner=lambda farm_id: OWNER,
        is_member=lambda farm_id, user_id: user_id == MEMBER,
        find_bovine=lambda farm_id, bovine_id: object() if bovine_id == bovine_in_farm else None,
    )

    check(FARM, bovine_id=bovine_in_farm, land_plot_id=FARM, member_user_id=MEMBER)
    check(FARM, member_user_id=OWNER)  # el dueño siempre pertenece
    for kwargs, message in (
        ({"bovine_id": uuid.uuid4()}, scope_rules.BOVINE_NOT_IN_FARM),
        ({"land_plot_id": uuid.uuid4()}, scope_rules.LAND_PLOT_NOT_IN_FARM),
        ({"member_user_id": STRANGER}, scope_rules.USER_NOT_IN_FARM),
    ):
        with pytest.raises(BusinessRuleError) as exc:
            check(FARM, **kwargs)
        assert exc.value.message == message

    without_finder = FarmScopeService(land_plot_exists=lambda f, lp: True, farm_owner=lambda f: None, is_member=lambda f, u: False)
    with pytest.raises(RuntimeError):
        without_finder(FARM, bovine_id=bovine_in_farm)


def test_scope_errors_reach_the_client_as_400() -> None:
    """Antes el validador lanzaba HTTPException; ahora es un error de dominio con el mismo resultado."""
    from fastapi import FastAPI

    from app.core.error_handlers import register_error_handlers

    mini = FastAPI()
    register_error_handlers(mini)
    check = FarmScopeService(land_plot_exists=lambda f, lp: False, farm_owner=lambda f: None, is_member=lambda f, u: False)

    @mini.post("/x")
    def x() -> None:
        check(FARM, land_plot_id=uuid.uuid4())

    response = TestClient(mini).post("/x")
    assert (response.status_code, response.json()) == (400, {"detail": scope_rules.LAND_PLOT_NOT_IN_FARM})


# ═══════════════════════════════════════════════════════════════
# Frontera
# ═══════════════════════════════════════════════════════════════


def test_farm_routes_are_served_by_the_module() -> None:
    from app.main import app
    from app.modules.farms.dependencies import get_catalog_service
    from app.modules.farms.service import CatalogService
    from app.modules.identity import get_current_user

    catalogs = SimpleNamespace(departments=lambda: [SimpleNamespace(id=DEPT, name="Córdoba", code="23")],
                               cities=lambda d: [], purposes=lambda: [])
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=OWNER)
    app.dependency_overrides[get_catalog_service] = lambda: CatalogService(catalogs)
    try:
        response = TestClient(app).get("/api/v1/farms/departments")
    finally:
        app.dependency_overrides.clear()
    assert response.json() == [{"id": str(DEPT), "name": "Córdoba", "code": "23"}]


def test_http_bulk_returns_the_report_and_422_points_to_the_bad_row() -> None:
    from app.main import app
    from app.modules.farms.dependencies import get_farm_service
    from app.modules.identity import get_current_user

    repo = FakeFarms(_existing_farm(farm_identifier="F-EXISTE"))
    service, _ = _farm_service(repo)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=OWNER)
    app.dependency_overrides[get_farm_service] = lambda: service
    body = lambda **kw: _farm_data(**kw).model_dump(mode="json")  # noqa: E731
    try:
        http = TestClient(app)
        ok = http.post("/api/v1/farms/bulk", json={"items": [body(name="Alfa", farm_identifier="F-A"),
                                                            body(name="Beta", farm_identifier="F-EXISTE")]})
        bad = http.post("/api/v1/farms/bulk", json={"items": [body(farm_identifier="F-Z"), body(farm_identifier="F-Y") | {"name": "x"}]})
    finally:
        app.dependency_overrides.clear()

    report = ok.json()
    assert ok.status_code == 200
    assert (report["total"], report["created"], report["failed"]) == (2, 1, 1)
    assert report["items"][0]["farm_identifier"] == "F-A"
    assert report["errors"] == [{"row": 2, "farm_identifier": "F-EXISTE", "error": farm_rules.FARM_IDENTIFIER_TAKEN}]
    assert bad.status_code == 422 and bad.json()["detail"][0]["loc"][:4] == ["body", "items", 1, "name"]  # fila 2 (índice 1)


def test_farms_only_loads_identity_and_boots_like_uvicorn() -> None:
    import subprocess
    import sys

    code = (
        "import sys, app.modules.farms.router, app.modules.farms.dependencies\n"
        "loaded = sorted({m.split('.')[2] for m in sys.modules if m.startswith('app.modules.') and m.count('.') >= 2})\n"
        "assert loaded == ['farms', 'identity'], loaded\n"
        "import app.main\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr[-1500:]
