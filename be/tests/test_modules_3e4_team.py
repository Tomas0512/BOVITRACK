"""
Pruebas de la Parte 3e-4 del refactor: módulo team (equipo de la finca).

Todas contra tablas reales (SQLite), con identity entregando usuarios, roles y
membresías por su puerto (MembershipDirectory) y farms el nombre de la finca:
  - Empleados: listar, cambiar rol/estado, cerrar/abrir cuenta, desvincular, y la
    regla "una finca nunca se queda sin Administrador" (incluye el bug #20).
  - Invitaciones: invitar, ver, registrarse o vincularse (incluye el bug #21).
  - Reactivación: solicitud pública y guard de moderadores.
  - Frontera: team solo carga identity y farms; sus rutas las sirve el módulo.
"""

import asyncio
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todas las tablas
from app.modules.team.schemas import EmployeeUpdate, InvitationCreate, InvitedRegister
from app.modules.team.service import EmployeeService, InvitationService, ReactivationService
from app.modules.team.service import employees as employee_rules
from app.modules.team.service import invitations as invitation_rules
from app.modules.team.service import reactivation as reactivation_rules
from app.shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError

FARM, OTHER_FARM = uuid.uuid4(), uuid.uuid4()
PASSWORD = "Clave#2026"


@pytest.fixture
def team() -> Iterator[SimpleNamespace]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base
    from app.modules import farms
    from app.modules.identity.models import Permission, Role, User, UserFarm
    from app.modules.identity.repository import MembershipDirectory
    from app.modules.team.repository import InvitationRepository, ReactivationRepository, Transaction

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for name in ("users", "role", "permission", "farm", "user_farm", "farm_invitation", "reactivation_request", "audit_log"):
        Base.metadata.tables[name].create(engine)
    now = datetime(2026, 11, 22, tzinfo=timezone.utc)
    with Session(engine) as db:
        def user(name: str, active: bool = True) -> Any:
            u = User(id=uuid.uuid4(), first_name=name.title(), last_name="Ruiz", document_type="CC",
                     document_number=f"DOC-{name}", email=f"{name}@x.com", phone="300", hashed_password="h",
                     is_active=active, token_version=0, created_at=now, updated_at=now)
            db.add(u)
            return u

        admin, empleado = Role(name="Administrador"), Role(name="Empleado")
        db.add_all([admin, empleado])
        ana, luis, rosa = user("ana"), user("luis"), user("rosa", active=False)
        db.flush()
        db.add(Permission(role_id=admin.id, module="usuarios", can_create=True, can_read=True, can_update=True, can_delete=True))
        farm = Base.metadata.tables["farm"]
        for fid, name in ((FARM, "La Esperanza"), (OTHER_FARM, "El Retiro")):
            db.execute(farm.insert(), [{"id": fid, "name": name, "owner_id": ana.id, "address": "x", "department_id": uuid.uuid4(),
                                        "city_municipality": "x", "total_area": 1, "area_unit": "hectareas",
                                        "purpose_id": uuid.uuid4(), "farm_identifier": name, "is_active": True,
                                        "created_at": now, "updated_at": now}])
        db.add_all([
            UserFarm(user_id=ana.id, farm_id=FARM, role_id=admin.id, assigned_at=now),
            UserFarm(user_id=luis.id, farm_id=FARM, role_id=empleado.id, assigned_at=now + timedelta(hours=1)),
            UserFarm(user_id=luis.id, farm_id=OTHER_FARM, role_id=empleado.id, assigned_at=now),
            UserFarm(user_id=rosa.id, farm_id=FARM, role_id=empleado.id, is_active=False, assigned_at=now),
        ])
        db.commit()

        audits: list[dict] = []
        sent: list[dict] = []

        async def send_invitation(**kw: Any) -> None:
            sent.append(kw)

        directory, tx = MembershipDirectory(db), Transaction(db)
        record = lambda **kw: audits.append(kw)  # noqa: E731
        yield SimpleNamespace(
            db=db, ana=ana, luis=luis, rosa=rosa, admin=admin, empleado=empleado, audits=audits, sent=sent,
            employees=EmployeeService(directory, tx, record_audit=record),
            invitations=InvitationService(InvitationRepository(db), directory, tx, farm_name=farms.build_farm_name_lookup(db),
                                          hash_password=lambda p: f"hash:{p}", send_invitation=send_invitation, record_audit=record),
            reactivation=ReactivationService(ReactivationRepository(db), directory, tx, record_audit=record),
        )


# ═══════════════════════════════════════════════════════════════
# Empleados
# ═══════════════════════════════════════════════════════════════


def test_list_employees_with_account_state_and_other_farms(team: SimpleNamespace) -> None:
    rows = team.employees.list(FARM)

    assert [r.first_name for r in rows] == ["Luis", "Ana", "Rosa"]  # el más reciente primero
    luis = rows[0]
    assert (luis.role_name, luis.is_active, luis.account_active, luis.other_farms_count) == ("Empleado", True, True, 1)
    assert [r.first_name for r in team.employees.list(FARM, is_active=False)] == ["Rosa"]
    assert [r.name for r in team.employees.roles()] == ["Administrador", "Empleado"]


def test_farm_never_loses_its_last_admin(team: SimpleNamespace) -> None:
    with pytest.raises(BusinessRuleError) as exc:
        team.employees.update(FARM, team.ana.id, EmployeeUpdate(is_active=False), team.ana.id)
    assert exc.value.message == employee_rules.LAST_ADMIN
    with pytest.raises(BusinessRuleError):
        team.employees.remove(FARM, team.ana.id, team.ana.id)

    # Con un segundo administrador, ya se puede
    team.employees.update(FARM, team.luis.id, EmployeeUpdate(role_id=team.admin.id), team.ana.id)
    assert team.employees.update(FARM, team.ana.id, EmployeeUpdate(is_active=False), team.luis.id).is_active is False


def test_bugfix_20_last_admin_cannot_lose_the_admin_role(team: SimpleNamespace) -> None:
    """Regresión #20: antes se le podía cambiar el rol al único Administrador y la finca quedaba sin admin."""
    with pytest.raises(BusinessRuleError) as exc:
        team.employees.update(FARM, team.ana.id, EmployeeUpdate(role_id=team.empleado.id), team.ana.id)
    assert exc.value.message == employee_rules.LAST_ADMIN_ROLE
    # cambiar el rol de alguien que no es admin, o "cambiar" al mismo rol, sigue permitido
    assert team.employees.update(FARM, team.ana.id, EmployeeUpdate(role_id=team.admin.id), team.ana.id).role_name == "Administrador"
    with pytest.raises(NotFoundError):
        team.employees.update(FARM, team.luis.id, EmployeeUpdate(role_id=uuid.uuid4()), team.ana.id)


def test_account_status_rules(team: SimpleNamespace) -> None:
    with pytest.raises(PermissionDeniedError) as exc:  # Luis no es admin de la finca
        team.employees.set_account_status(FARM, team.rosa.id, is_active=True, reason=None, actor_id=team.luis.id)
    assert exc.value.message == employee_rules.ONLY_ADMIN_CLOSES_ACCOUNTS
    with pytest.raises(BusinessRuleError) as exc:
        team.employees.set_account_status(FARM, team.ana.id, is_active=False, reason=None, actor_id=team.ana.id)
    assert exc.value.message == employee_rules.OWN_ACCOUNT

    closed = team.employees.set_account_status(FARM, team.luis.id, is_active=False, reason="renunció", actor_id=team.ana.id)
    assert (closed.account_active, team.luis.token_version) == (False, 1)  # sesiones anuladas
    assert team.audits[-1] == {"user_id": str(team.ana.id), "farm_id": str(FARM), "action": "deactivate_account",
                               "entity": "user", "entity_id": str(team.luis.id), "details": {"reason": "renunció"}}
    before = len(team.audits)
    team.employees.set_account_status(FARM, team.luis.id, is_active=False, reason=None, actor_id=team.ana.id)
    assert len(team.audits) == before  # ya estaba cerrada: nada que auditar


def test_remove_employee(team: SimpleNamespace) -> None:
    team.employees.remove(FARM, team.luis.id, team.ana.id)

    assert [r.first_name for r in team.employees.list(FARM)] == ["Ana", "Rosa"]
    with pytest.raises(NotFoundError) as exc:
        team.employees.remove(FARM, team.luis.id, team.ana.id)
    assert exc.value.message == employee_rules.EMPLOYEE_NOT_FOUND


# ═══════════════════════════════════════════════════════════════
# Invitaciones
# ═══════════════════════════════════════════════════════════════


def _invite(team: SimpleNamespace, email: str, role: Any = None, by: Any = None, farm: uuid.UUID = FARM) -> Any:
    data = InvitationCreate(email=email, role_id=(role or team.empleado).id)
    return asyncio.run(team.invitations.invite(farm, data, (by or team.ana).id))


def _register(token: str, **overrides: Any) -> InvitedRegister:
    data: dict[str, Any] = {"token": token, "first_name": "Pedro", "last_name": "Mora", "document_type": "CC",
                            "document_number": "DOC-pedro", "phone": "301", "password": PASSWORD,
                            "confirm_password": PASSWORD, "accept_terms": True, "accept_data_policy": True}
    data.update(overrides)
    return InvitedRegister(**data)


def test_invite_rules(team: SimpleNamespace) -> None:
    with pytest.raises(NotFoundError) as exc:
        _invite(team, "x@x.com", farm=uuid.uuid4())
    assert exc.value.message == invitation_rules.FARM_NOT_FOUND
    with pytest.raises(PermissionDeniedError) as exc:  # un empleado no ofrece el rol Administrador
        _invite(team, "x@x.com", role=team.admin, by=team.luis)
    assert exc.value.message == invitation_rules.ONLY_ADMIN_GRANTS_ADMIN
    with pytest.raises(ConflictError):
        _invite(team, "luis@x.com")


def test_bugfix_21_invitation_audit_keeps_the_real_id(team: SimpleNamespace) -> None:
    """Regresión #21: la auditoría guardaba entity_id="None" porque se escribía antes de tener id."""
    first = _invite(team, " Pedro@X.com ")
    second = _invite(team, "pedro@x.com")

    assert team.audits[-1]["entity_id"] == str(second.id) != "None"
    assert team.sent[-1] == {"email": "pedro@x.com", "token": team.sent[-1]["token"], "farm_name": "La Esperanza"}
    from app.modules.team.models import FarmInvitation
    assert team.db.get(FarmInvitation, first.id).used is True  # la anterior quedó anulada


def test_register_by_invitation_creates_and_links_the_user(team: SimpleNamespace) -> None:
    _invite(team, "pedro@x.com")
    token = team.sent[-1]["token"]

    info = team.invitations.info(token)
    assert (info.email, info.farm_name, info.role_name, info.inviter_name) == ("pedro@x.com", "La Esperanza", "Empleado", "Ana Ruiz")

    with pytest.raises(BusinessRuleError) as exc:  # documento de otra persona
        team.invitations.register_invited(_register(token, document_number="DOC-ana"))
    assert exc.value.message == invitation_rules.DOCUMENT_TAKEN
    pedro = team.invitations.register_invited(_register(token))
    assert (pedro.hashed_password, pedro.email_verified) == (f"hash:{PASSWORD}", True)
    assert "Pedro" in [r.first_name for r in team.employees.list(FARM)]
    with pytest.raises(BusinessRuleError) as exc:  # un solo uso
        team.invitations.register_invited(_register(token))
    assert exc.value.message == invitation_rules.INVITATION_USED


def test_existing_user_is_only_linked_and_expired_invitations_fail(team: SimpleNamespace) -> None:
    from app.modules.identity.models import UserFarm

    # Luis tiene cuenta pero se le quita la membresía de OTHER_FARM: la invitación solo debe vincularlo
    team.db.query(UserFarm).filter_by(user_id=team.luis.id, farm_id=OTHER_FARM).delete()
    team.db.commit()
    _invite(team, "luis@x.com", farm=OTHER_FARM)
    linked = team.invitations.register_invited(_register(team.sent[-1]["token"]))
    assert linked.id == team.luis.id and team.audits[-1]["action"] == "join_farm_by_invitation"

    _invite(team, "nuevo@x.com")
    from app.modules.team.models import FarmInvitation
    invitation = team.db.query(FarmInvitation).filter_by(email="nuevo@x.com").one()
    invitation.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    team.db.commit()
    with pytest.raises(BusinessRuleError) as exc:
        team.invitations.info(invitation.token)
    assert exc.value.message == invitation_rules.INVITATION_EXPIRED
    with pytest.raises(NotFoundError):
        team.invitations.info("no-existe")


# ═══════════════════════════════════════════════════════════════
# Reactivación
# ═══════════════════════════════════════════════════════════════


def _pending_requests(team: SimpleNamespace) -> list[Any]:
    from app.modules.team.models import ReactivationRequest

    return list(team.db.query(ReactivationRequest).filter_by(status="pending"))


def test_request_reactivation_rules(team: SimpleNamespace) -> None:
    # Correo inexistente o cuenta activa: no pasa nada y no hay error (no se revela nada).
    assert team.reactivation.request("nadie@x.com", None) is None
    assert team.reactivation.request("ana@x.com", None) is None
    assert _pending_requests(team) == []

    # Cuenta desactivada: se crea la solicitud (correo normalizado); una pendiente a la vez.
    team.reactivation.request(" ROSA@x.com ", "volví a la finca")
    team.reactivation.request("rosa@x.com", None)
    [request] = _pending_requests(team)
    assert (request.user_id, request.reason) == (team.rosa.id, "volví a la finca")

    with pytest.raises(PermissionDeniedError):
        team.reactivation.ensure_reviewer(team.luis.id)  # no es admin de ninguna finca
    team.reactivation.ensure_reviewer(team.ana.id)
    assert [r.user_name for r in team.reactivation.list_pending(team.ana.id)] == ["Rosa Ruiz"]


# ═══════════════════════════════════════════════════════════════
# Frontera
# ═══════════════════════════════════════════════════════════════


def test_team_routes_are_served_by_the_module(team: SimpleNamespace) -> None:
    from app.core.database import get_db
    from app.main import app
    from app.modules.identity import get_current_user

    who = {"user": team.luis}
    app.dependency_overrides[get_db] = lambda: team.db
    app.dependency_overrides[get_current_user] = lambda: who["user"]
    try:
        http = TestClient(app)
        denied = http.get("/api/v1/admin/reactivation-requests")
        assert (denied.status_code, denied.json()) == (403, {"detail": reactivation_rules.ONLY_ADMIN_REVIEWS})
        who["user"] = team.ana
        assert http.get("/api/v1/admin/reactivation-requests").json() == []
        employees = http.get(f"/api/v1/farms/{FARM}/employees")
        assert employees.status_code == 200 and len(employees.json()) == 3
        public = http.get("/api/v1/auth/invitation/no-existe")
        assert (public.status_code, public.json()) == (404, {"detail": invitation_rules.INVITATION_NOT_FOUND})
    finally:
        app.dependency_overrides.clear()


def test_request_reactivation_answers_the_same_for_any_email(team: SimpleNamespace) -> None:
    """Parte 6b: la ruta pública no revela si un correo existe ni si la cuenta está activa."""
    from app.core.database import get_db
    from app.core.limiter import limiter
    from app.main import app

    app.dependency_overrides[get_db] = lambda: team.db
    was_enabled, limiter.enabled = limiter.enabled, False  # 3/minuto: aquí se hacen 3 seguidas
    try:
        http = TestClient(app)
        answers = [http.post("/api/v1/auth/request-reactivation", json={"email": email})
                   for email in ("nadie@x.com", "ana@x.com", "rosa@x.com")]  # no existe, activa, desactivada
        assert {(r.status_code, r.text) for r in answers} == {
            (202, '{"message":"' + reactivation_rules.REQUEST_RECEIVED + '"}'),
        }
        assert [r.user_id for r in _pending_requests(team)] == [team.rosa.id]  # solo la que aplica
    finally:
        app.dependency_overrides.clear()
        limiter.enabled = was_enabled


def test_team_only_loads_identity_and_farms_and_boots_like_uvicorn() -> None:
    import subprocess
    import sys

    code = (
        "import sys, app.modules.team.router, app.modules.team.dependencies\n"
        "loaded = sorted({m.split('.')[2] for m in sys.modules if m.startswith('app.modules.') and m.count('.') >= 2})\n"
        "assert loaded == ['farms', 'identity', 'team'], loaded\n"
        "import app.main\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr[-1500:]
