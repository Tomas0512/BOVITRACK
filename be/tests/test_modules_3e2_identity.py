"""
Pruebas de la Parte 3e-2 del refactor: módulo identity (la capa base).

  - AuthService: registro, login con bloqueo por intentos, access/refresh token,
    recuperación de contraseña y verificación de correo (fakes, sin BD ni SMTP).
  - AccountService: perfil y baja de la cuenta propia.
  - AccessService + repositorio contra tablas reales (SQLite): la regla RBAC de
    require_permission, el rol más reciente y "último administrador".
  - Frontera HTTP: 401 con WWW-Authenticate, guards reales en una mini-app y las
    rutas /api/v1/auth y /api/v1/users/me servidas por el módulo.
"""

import asyncio
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — registra todas las tablas
from app.core.error_handlers import register_error_handlers
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.modules.identity.models import User
from app.modules.identity.schemas import ResetPasswordRequest, UserCreate, UserLogin
from app.modules.identity.service import AccessService, AccountService, AuthService, LoginThrottle
from app.modules.identity.service import access as access_rules
from app.modules.identity.service import account as account_rules
from app.modules.identity.service import auth as auth_rules
from app.shared.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    PermissionDeniedError,
    TooManyAttemptsError,
)

PASSWORD = "Clave#2026"


# ═══════════════════════════════════════════════════════════════
# Fakes
# ═══════════════════════════════════════════════════════════════


def _user(**overrides: Any) -> User:
    data: dict[str, Any] = {
        "id": uuid.uuid4(), "email": "ana@x.com", "first_name": "Ana", "last_name": "Ruiz",
        "document_type": "CC", "document_number": "1001", "phone": "300",
        "hashed_password": hash_password(PASSWORD), "is_active": True, "email_verified": False,
        "token_version": 0, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return User(**data)


class FakeUsers:
    def __init__(self, *users: User) -> None:
        self.users = {u.id: u for u in users}
        self.reset_tokens: dict[str, SimpleNamespace] = {}
        self.verify_tokens: dict[str, SimpleNamespace] = {}
        self.log: list[str] = []

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    def get_by_document(self, document_number: str) -> User | None:
        return next((u for u in self.users.values() if u.document_number == document_number), None)

    def add(self, user: User) -> None:
        self.log.append("add")
        self._pending = user

    def flush(self) -> None:
        self.log.append("flush")
        user = self._pending
        user.id = user.id or uuid.uuid4()
        self.users[user.id] = user

    def add_password_reset_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        self.reset_tokens[token] = SimpleNamespace(user_id=user_id, token=token, expires_at=expires_at, used=False)

    def get_password_reset_token(self, token: str) -> SimpleNamespace | None:
        return self.reset_tokens.get(token)

    def add_email_verification_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        self.verify_tokens[token] = SimpleNamespace(user_id=user_id, token=token, expires_at=expires_at, used=False)

    def get_email_verification_token(self, token: str) -> SimpleNamespace | None:
        return self.verify_tokens.get(token)

    def commit(self) -> None:
        self.log.append("commit")

    def refresh(self, user: User) -> None:
        pass


class Outbox:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def __call__(self, email: str, token: str) -> None:
        self.sent.append((email, token))


def _auth(users: FakeUsers, throttle: LoginThrottle | None = None) -> tuple[AuthService, list[dict[str, Any]], Outbox, Outbox]:
    audits: list[dict[str, Any]] = []
    resets, verifications = Outbox(), Outbox()
    service = AuthService(
        users,
        throttle=throttle or LoginThrottle(),
        record_audit=lambda **kw: (users.log.append("audit"), audits.append(kw)),
        send_password_reset=resets,
        send_email_verification=verifications,
    )
    return service, audits, resets, verifications


def _signup(**overrides: Any) -> UserCreate:
    data: dict[str, Any] = {
        "email": "Nuevo@X.com", "first_name": "Luis", "last_name": "Mora", "document_type": "CC",
        "document_number": " 2002 ", "phone": "301", "password": PASSWORD, "confirm_password": PASSWORD,
        "accept_terms": True, "accept_data_policy": True,
    }
    data.update(overrides)
    return UserCreate(**data)


# ═══════════════════════════════════════════════════════════════
# AuthService
# ═══════════════════════════════════════════════════════════════


def test_register_normalizes_hashes_and_audits_in_one_transaction() -> None:
    users = FakeUsers()
    service, audits, _, _ = _auth(users)

    user = service.register(_signup())

    assert (user.email, user.document_number) == ("nuevo@x.com", "2002")
    assert user.hashed_password != PASSWORD and user.accepted_terms_at is not None
    # el usuario se inserta (flush) ANTES de auditar, y todo se confirma una sola vez
    assert users.log == ["add", "flush", "audit", "commit"]
    assert audits == [{"user_id": str(user.id), "action": "register", "entity": "user",
                       "entity_id": str(user.id), "details": {"email": "nuevo@x.com"}}]
    # Bug corregido: registrar ya no deja un token de verificación huérfano (antes se creaban dos)
    assert users.verify_tokens == {}


def test_register_rejects_duplicate_email_and_document() -> None:
    service, _, _, _ = _auth(FakeUsers(_user(email="nuevo@x.com", document_number="9")))
    with pytest.raises(BusinessRuleError) as exc:
        service.register(_signup())
    assert exc.value.message == auth_rules.EMAIL_TAKEN

    service, _, _, _ = _auth(FakeUsers(_user(email="otro@x.com", document_number="2002")))
    with pytest.raises(BusinessRuleError) as exc:
        service.register(_signup())
    assert exc.value.message == auth_rules.DOCUMENT_TAKEN


def test_verification_email_sends_exactly_one_token_and_verifies() -> None:
    user = _user()
    users = FakeUsers(user)
    service, audits, _, verifications = _auth(users)

    asyncio.run(service.send_verification_email(user.id))

    assert len(users.verify_tokens) == 1 and verifications.sent == [(user.email, next(iter(users.verify_tokens)))]
    token = next(iter(users.verify_tokens))
    service.verify_email(token)
    assert user.email_verified and users.verify_tokens[token].used and audits[-1]["action"] == "email_verified"
    with pytest.raises(BusinessRuleError) as exc:  # un solo uso
        service.verify_email(token)
    assert exc.value.message == auth_rules.VERIFY_TOKEN_INVALID


def test_login_locks_the_email_after_five_failures_and_success_resets() -> None:
    now = [datetime(2026, 11, 22, 8, 0, tzinfo=timezone.utc)]
    user = _user()
    service, _, _, _ = _auth(FakeUsers(user), LoginThrottle(clock=lambda: now[0]))
    wrong = UserLogin(email="ANA@x.com", password="mala")

    for _ in range(4):
        with pytest.raises(AuthenticationError):
            service.login(wrong)
    assert service.login(UserLogin(email="ana@x.com", password=PASSWORD)).token_type == "bearer"  # 4 fallos + éxito: limpia

    for _ in range(5):
        with pytest.raises(AuthenticationError) as exc:
            service.login(wrong)
    assert exc.value.message == auth_rules.INVALID_CREDENTIALS
    with pytest.raises(TooManyAttemptsError) as locked:  # ni la clave correcta entra
        service.login(UserLogin(email="ana@x.com", password=PASSWORD))
    assert locked.value.message == "Demasiados intentos fallidos. Intente de nuevo en 16 minuto(s)."

    now[0] += timedelta(minutes=15, seconds=1)
    assert service.login(UserLogin(email="ana@x.com", password=PASSWORD)).access_token


def test_login_of_a_disabled_account_is_403() -> None:
    service, _, _, _ = _auth(FakeUsers(_user(is_active=False)))
    with pytest.raises(PermissionDeniedError) as exc:
        service.login(UserLogin(email="ana@x.com", password=PASSWORD))
    assert exc.value.message == auth_rules.ACCOUNT_DISABLED_LOGIN


def test_access_token_rules() -> None:
    user = _user(token_version=3)
    service, _, _, _ = _auth(FakeUsers(user))
    claims = {"sub": str(user.id), "ver": 3}

    assert service.authenticate(create_access_token(claims)) is user
    for bad in (
        "no-es-un-jwt",
        create_refresh_token(claims),  # un refresh no sirve como access
        create_access_token({"sub": str(user.id), "ver": 2}),  # sesión cerrada (logout-all)
        create_access_token({"sub": "no-es-uuid", "ver": 3}),  # antes: 500
        create_access_token({"sub": str(user.id)}),
    ):
        with pytest.raises(AuthenticationError) as exc:
            service.authenticate(bad)
        assert exc.value.message == auth_rules.COULD_NOT_VALIDATE

    user.is_active = False
    with pytest.raises(PermissionDeniedError) as denied:
        service.authenticate(create_access_token(claims))
    assert denied.value.message == auth_rules.ACCOUNT_DISABLED


def test_refresh_and_logout_all_invalidate_old_tokens() -> None:
    user = _user()
    service, audits, _, _ = _auth(FakeUsers(user))
    old_refresh = create_refresh_token({"sub": str(user.id), "ver": 0})

    assert service.refresh(old_refresh).refresh_token
    service.logout_all(user)

    assert user.token_version == 1 and audits[-1]["action"] == "logout_all_sessions"
    with pytest.raises(AuthenticationError) as exc:
        service.refresh(old_refresh)
    assert exc.value.message == auth_rules.INVALID_REFRESH
    with pytest.raises(AuthenticationError) as exc:
        service.refresh(create_access_token({"sub": str(user.id), "ver": 1}))
    assert exc.value.message == auth_rules.INVALID_REFRESH


def test_password_reset_flow() -> None:
    user = _user()
    users = FakeUsers(user)
    service, audits, resets, _ = _auth(users)

    asyncio.run(service.request_password_reset("nadie@x.com"))  # no revela si existe
    assert resets.sent == []
    asyncio.run(service.request_password_reset(" ANA@x.com "))
    (email, token), = resets.sent
    assert email == "ana@x.com"

    new = "Nueva#2027"
    service.reset_password(ResetPasswordRequest(token=token, new_password=new, confirm_password=new))
    assert audits[-1]["action"] == "password_reset"
    assert service.login(UserLogin(email="ana@x.com", password=new)).access_token

    for tok, message in ((token, auth_rules.RESET_TOKEN_USED), ("x", auth_rules.RESET_TOKEN_INVALID)):
        with pytest.raises(BusinessRuleError) as exc:
            service.reset_password(ResetPasswordRequest(token=tok, new_password=new, confirm_password=new))
        assert exc.value.message == message

    users.add_password_reset_token(user.id, "viejo", datetime.now(timezone.utc) - timedelta(minutes=1))
    with pytest.raises(BusinessRuleError) as exc:
        service.reset_password(ResetPasswordRequest(token="viejo", new_password=new, confirm_password=new))
    assert exc.value.message == auth_rules.RESET_TOKEN_EXPIRED


# ═══════════════════════════════════════════════════════════════
# AccountService
# ═══════════════════════════════════════════════════════════════


class FakeMemberships:
    def __init__(self, role: str | None = "Capataz", last_admin_of: list[uuid.UUID] | None = None) -> None:
        self.role, self.last_admin_of, self.commits = role, last_admin_of or [], 0

    def latest_role_name(self, user_id: uuid.UUID) -> str | None:
        return self.role

    def farms_where_last_admin(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        return self.last_admin_of

    def commit(self) -> None:
        self.commits += 1


def test_profile_includes_latest_role() -> None:
    user = _user()
    assert AccountService(FakeMemberships("Capataz"), record_audit=lambda **kw: None).profile(user).role_name == "Capataz"
    assert AccountService(FakeMemberships(None), record_audit=lambda **kw: None).profile(user).role_name is None


def test_delete_account_rules() -> None:
    user = _user()
    audits: list[dict[str, Any]] = []
    service = AccountService(FakeMemberships(last_admin_of=[uuid.uuid4()]), record_audit=lambda **kw: audits.append(kw))

    with pytest.raises(BusinessRuleError) as exc:
        service.delete_account(user, "borrar")
    assert exc.value.message == account_rules.MUST_CONFIRM
    with pytest.raises(BusinessRuleError) as exc:
        service.delete_account(user, " eliminar ")
    assert exc.value.message == account_rules.LAST_ADMIN and user.is_active and audits == []

    memberships = FakeMemberships()
    AccountService(memberships, record_audit=lambda **kw: audits.append(kw)).delete_account(user, " eliminar ")
    assert (user.is_active, user.token_version, memberships.commits) == (False, 1, 1)
    assert audits[-1]["action"] == "delete_account"


# ═══════════════════════════════════════════════════════════════
# AccessService (regla RBAC)
# ═══════════════════════════════════════════════════════════════


class FakeAccess:
    def __init__(self, membership: Any = None, role: Any = None, permission: Any = None) -> None:
        self.m, self.r, self.p = membership, role, permission

    def active_membership(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> Any:
        return self.m

    def role(self, role_id: uuid.UUID) -> Any:
        return self.r

    def permission(self, role_id: uuid.UUID, module: str) -> Any:
        return self.p

    def has_permission_anywhere(self, user_id: uuid.UUID, module: str, action: str) -> bool:
        return False


def test_access_rule_messages() -> None:
    uid, fid = uuid.uuid4(), uuid.uuid4()
    member, active = SimpleNamespace(role_id=uuid.uuid4()), SimpleNamespace(is_active=True)
    can_read = SimpleNamespace(can_read=True, can_delete=False)
    cases = [
        (FakeAccess(), access_rules.NO_FARM_ACCESS),
        (FakeAccess(member, None), access_rules.ROLE_DISABLED),
        (FakeAccess(member, SimpleNamespace(is_active=False)), access_rules.ROLE_DISABLED),
        (FakeAccess(member, active, None), "Tu rol no tiene permisos para el módulo 'bovinos'"),
        (FakeAccess(member, active, can_read), "No tienes permiso para 'can_delete' en 'bovinos'"),
    ]
    for store, message in cases:
        with pytest.raises(PermissionDeniedError) as exc:
            AccessService(store).check_permission(uid, fid, "bovinos", "can_delete")
        assert exc.value.message == message

    AccessService(FakeAccess(member, active, can_read)).check_permission(uid, fid, "bovinos", "can_read")


# ═══════════════════════════════════════════════════════════════
# Repositorio + guards contra tablas reales (SQLite)
# ═══════════════════════════════════════════════════════════════

ANA, LUIS = uuid.uuid4(), uuid.uuid4()
FARM, OTHER = uuid.uuid4(), uuid.uuid4()


@pytest.fixture
def identity_tables() -> Iterator[Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base
    from app.modules.identity.models import Permission, Role, UserFarm

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for name in ("users", "role", "permission", "farm", "user_farm"):
        Base.metadata.tables[name].create(engine)
    now = datetime(2026, 11, 22, tzinfo=timezone.utc)
    with Session(engine) as db:
        db.add_all([_user(id=ANA), _user(id=LUIS, email="luis@x.com", document_number="2")])
        admin, capataz = Role(name="Administrador"), Role(name="Capataz")
        db.add_all([admin, capataz])
        db.flush()
        db.add_all([
            Permission(role_id=admin.id, module="bovinos", can_create=True, can_read=True, can_update=True, can_delete=True),
            Permission(role_id=capataz.id, module="bovinos", can_create=False, can_read=True),
        ])
        farm = Base.metadata.tables["farm"]
        for fid in (FARM, OTHER):
            db.execute(farm.insert(), [{"id": fid, "name": str(fid), "owner_id": ANA, "is_active": True, "address": "x",
                                        "department_id": uuid.uuid4(), "city_municipality": "x", "total_area": 1,
                                        "purpose_id": uuid.uuid4(), "farm_identifier": str(fid),
                                        "created_at": now, "updated_at": now}])
        db.add_all([
            UserFarm(user_id=ANA, farm_id=FARM, role_id=admin.id, assigned_at=now),
            UserFarm(user_id=ANA, farm_id=OTHER, role_id=capataz.id, assigned_at=now + timedelta(days=1)),
            UserFarm(user_id=LUIS, farm_id=OTHER, role_id=admin.id, assigned_at=now),
        ])
        db.commit()
        yield db


def test_membership_repository_queries(identity_tables: Any) -> None:
    from app.modules.identity.repository import MembershipRepository, UserRepository

    repo = MembershipRepository(identity_tables)

    assert repo.latest_role_name(ANA) == "Capataz"  # la membresía más reciente
    assert repo.farms_where_last_admin(ANA) == [FARM]  # en OTHER el admin es Luis
    assert repo.farms_where_last_admin(LUIS) == [OTHER]
    assert repo.has_permission_anywhere(ANA, "bovinos", "can_delete")
    assert not repo.has_permission_anywhere(ANA, "tareas", "can_read")
    assert sorted(repo.active_member_ids(OTHER)) == sorted([ANA, LUIS])
    assert repo.is_member(FARM, ANA) and not repo.is_member(FARM, LUIS)
    assert UserRepository(identity_tables).email_of(LUIS) == "luis@x.com"


def test_require_permission_guard_against_real_tables(identity_tables: Any) -> None:
    from app.core.database import get_db
    from app.modules.identity import get_current_user, require_permission

    mini = FastAPI()
    register_error_handlers(mini)

    @mini.delete("/farms/{farm_id}/bovines", dependencies=[Depends(require_permission("bovinos", "can_delete"))])
    def delete_bovines(farm_id: uuid.UUID) -> dict[str, str]:
        return {"ok": str(farm_id)}

    who = {"id": ANA}
    mini.dependency_overrides[get_db] = lambda: identity_tables
    mini.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=who["id"])
    http = TestClient(mini)

    assert http.delete(f"/farms/{FARM}/bovines").status_code == 200  # Administrador
    capataz = http.delete(f"/farms/{OTHER}/bovines")  # Capataz: solo lectura
    assert (capataz.status_code, capataz.json()) == (403, {"detail": "No tienes permiso para 'can_delete' en 'bovinos'"})
    who["id"] = LUIS
    outsider = http.delete(f"/farms/{FARM}/bovines")
    assert (outsider.status_code, outsider.json()) == (403, {"detail": access_rules.NO_FARM_ACCESS})


# ═══════════════════════════════════════════════════════════════
# Frontera HTTP de la app
# ═══════════════════════════════════════════════════════════════


def test_bad_token_is_401_with_www_authenticate() -> None:
    from app.main import app

    response = TestClient(app).get("/api/v1/users/me", headers={"Authorization": "Bearer basura"})

    assert (response.status_code, response.json()) == (401, {"detail": auth_rules.COULD_NOT_VALIDATE})
    assert response.headers["www-authenticate"] == "Bearer"


def test_identity_routes_are_served_by_the_module() -> None:
    from app.main import app
    from app.modules.identity import get_current_user
    from app.modules.identity.dependencies import get_account_service, get_auth_service

    user = _user()
    service, _, _, _ = _auth(FakeUsers(user))
    app.dependency_overrides[get_auth_service] = lambda: service
    app.dependency_overrides[get_account_service] = lambda: AccountService(FakeMemberships("Empleado"), record_audit=lambda **kw: None)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        http = TestClient(app)
        wrong = http.post("/api/v1/auth/login", json={"email": "ana@x.com", "password": "mala"})
        assert (wrong.status_code, wrong.json()) == (401, {"detail": auth_rules.INVALID_CREDENTIALS})
        assert http.post("/api/v1/auth/login", json={"email": "ana@x.com", "password": PASSWORD}).status_code == 200
        me = http.get("/api/v1/users/me").json()
        assert (me["email"], me["role_name"]) == ("ana@x.com", "Empleado")
        bad = http.request("DELETE", "/api/v1/users/me", json={"confirmation_text": "no"})
        assert (bad.status_code, bad.json()) == (400, {"detail": account_rules.MUST_CONFIRM})
    finally:
        app.dependency_overrides.clear()


def test_identity_is_the_base_layer_and_boots_like_uvicorn() -> None:
    import subprocess
    import sys

    code = (
        "import sys, app.modules.identity, app.modules.identity.router\n"
        "others = sorted({m.split('.')[2] for m in sys.modules if m.startswith('app.modules.') and m.count('.') >= 2} - {'identity'})\n"
        "assert others == [], others\n"
        "import app.main\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr[-1500:]


def test_bugfix_16_inactive_member_cannot_be_assigned_a_task(identity_tables: Any) -> None:
    """Regresión #16: un empleado DESACTIVADO en la finca ya no recibe tareas.

    Antes bastaba con que existiera la fila en user_farm: la tarea se guardaba,
    pero el empleado no podía verla (require_permission le daba 403).
    """
    from app.modules import farms
    from app.modules.identity import build_membership_check
    from app.modules.identity.models import UserFarm

    is_member = build_membership_check(identity_tables)
    ensure_farm_scope = farms.build_farm_scope_checker(identity_tables)  # farms le pregunta a identity
    ensure_farm_scope(OTHER, member_user_id=LUIS)  # activo: pasa

    luis = identity_tables.query(UserFarm).filter_by(user_id=LUIS, farm_id=OTHER).one()
    luis.is_active = False  # el admin lo desactiva en la finca (la fila se queda)
    identity_tables.commit()

    assert not is_member(OTHER, LUIS)
    with pytest.raises(BusinessRuleError) as exc:  # 400
        ensure_farm_scope(OTHER, member_user_id=LUIS)
    assert exc.value.message == "El usuario asignado no pertenece a esta finca."
    # El dueño de la finca sigue pudiendo recibir tareas aunque no tenga membresía activa.
    identity_tables.query(UserFarm).filter_by(user_id=ANA, farm_id=OTHER).one().is_active = False
    identity_tables.commit()
    ensure_farm_scope(OTHER, member_user_id=ANA)
