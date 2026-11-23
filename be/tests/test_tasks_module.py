"""
Pruebas del módulo piloto `tasks` (Parte 2 del refactor).

¿Qué? Prueba cada capa por separado y luego la frontera HTTP completa:
      1. Servicio: con repositorio y colaboradores falsos (sin BD, sin FastAPI).
      2. Repositorio: contra SQLite en memoria con la tabla `task` real.
      3. Router: con TestClient, comprobando códigos de estado y cuerpos.
¿Para qué? Demostrar que el módulo cumple su contrato (README.md del módulo)
           y que la separación en capas permite probar el negocio sin
           infraestructura.
¿Impacto? Si alguien cambia el orden de la auditoría, el filtrado por finca,
          el 404 o el formato de respuesta, alguna de estas pruebas falla.
"""

import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 — registra todos los modelos (relaciones por nombre)
from app.modules.tasks.models import Task
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import TaskCreate, TaskUpdate
from app.modules.tasks.service import TASK_NOT_FOUND, TaskService
from app.shared.exceptions import NotFoundError

FARM = uuid.uuid4()
OTHER_FARM = uuid.uuid4()
USER = uuid.uuid4()
DUE = datetime(2026, 12, 1, tzinfo=timezone.utc)


# ═══════════════════════════════════════════════════════════════
# Dobles de prueba
# ═══════════════════════════════════════════════════════════════


class FakeTaskRepository:
    """Repositorio en memoria con la misma interfaz que TaskRepository."""

    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Task] = {}
        self.events: list[str] = []

    def get_in_farm(self, farm_id: uuid.UUID, task_id: uuid.UUID) -> Task | None:
        task = self.rows.get(task_id)
        return task if task is not None and task.farm_id == farm_id else None

    def list_by_farm(self, farm_id: uuid.UUID, **filters: Any) -> list[Task]:
        self.events.append(f"list:{sorted(k for k, v in filters.items() if v)}")
        return [t for t in self.rows.values() if t.farm_id == farm_id]

    def add(self, task: Task) -> None:
        task.id = task.id or uuid.uuid4()
        self.rows[task.id] = task
        self.events.append("add")

    def delete(self, task: Task) -> None:
        self.rows.pop(task.id)
        self.events.append("delete")

    def commit(self) -> None:
        self.events.append("commit")

    def refresh(self, task: Task) -> None:
        # Simula lo que hace la BD real al recargar: llenar las marcas de tiempo.
        now = datetime.now(timezone.utc)
        task.created_at = task.created_at or now
        task.updated_at = now
        self.events.append("refresh")


class Recorder:
    """Colaborador falso que guarda con qué argumentos lo llamaron."""

    def __init__(self, events: list[str] | None = None, name: str = "") -> None:
        self.calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self._events = events
        self._name = name

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append((args, kwargs))
        if self._events is not None:
            self._events.append(self._name)


def _make_service() -> tuple[TaskService, FakeTaskRepository, Recorder, Recorder]:
    repo = FakeTaskRepository()
    scope = Recorder()
    audit = Recorder(repo.events, "audit")
    return TaskService(repo, scope, audit), repo, scope, audit  # type: ignore[arg-type]


def _create_data(**overrides: Any) -> TaskCreate:
    values: dict[str, Any] = {
        "assigned_to": uuid.uuid4(),
        "title": "Vacunar lote 3",
        "task_type": "sanitaria",
        "due_date": DUE,
    }
    values.update(overrides)
    return TaskCreate(**values)


# ═══════════════════════════════════════════════════════════════
# 1. Servicio (negocio puro)
# ═══════════════════════════════════════════════════════════════


def test_create_checks_farm_scope_with_all_referenced_entities() -> None:
    service, _, scope, _ = _make_service()
    bovine, plot = uuid.uuid4(), uuid.uuid4()
    data = _create_data(bovine_id=bovine, land_plot_id=plot)

    service.create(FARM, data, USER)

    assert scope.calls == [
        ((FARM,), {"bovine_id": bovine, "land_plot_id": plot, "member_user_id": data.assigned_to})
    ]


def test_create_sets_assigner_saves_then_audits_in_original_order() -> None:
    service, repo, _, audit = _make_service()

    task = service.create(FARM, _create_data(), USER)

    assert task.farm_id == FARM
    assert task.assigned_by == USER
    assert repo.events == ["add", "commit", "refresh", "audit", "commit"]
    assert audit.calls[0][1] == {
        "user_id": str(USER),
        "farm_id": str(FARM),
        "action": "create",
        "entity": "task",
        "entity_id": str(task.id),
        "details": {"title": "Vacunar lote 3"},
    }


def test_create_does_not_save_when_scope_check_rejects() -> None:
    repo = FakeTaskRepository()

    def reject(*args: Any, **kwargs: Any) -> None:
        raise ValueError("bovino de otra finca")

    service = TaskService(repo, reject, Recorder())  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        service.create(FARM, _create_data(), USER)
    assert repo.rows == {}


def test_get_raises_not_found_for_task_of_another_farm() -> None:
    service, _, _, _ = _make_service()
    task = service.create(OTHER_FARM, _create_data(), USER)

    with pytest.raises(NotFoundError) as exc:
        service.get(FARM, task.id)
    assert exc.value.message == TASK_NOT_FOUND


def test_update_changes_only_sent_fields_and_audits_status() -> None:
    service, repo, _, audit = _make_service()
    task = service.create(FARM, _create_data(priority="alta"), USER)
    repo.events.clear()

    updated = service.update(FARM, task.id, TaskUpdate(status="completada"), USER)

    assert updated.status == "completada"
    assert updated.priority == "alta"
    assert repo.events == ["commit", "refresh", "audit", "commit"]
    assert audit.calls[-1][1]["details"] == {"title": "Vacunar lote 3", "status": "completada"}


def test_delete_audits_before_removing() -> None:
    service, repo, _, audit = _make_service()
    task = service.create(FARM, _create_data(), USER)
    repo.events.clear()

    service.delete(FARM, task.id, USER)

    assert repo.events == ["audit", "delete", "commit"]
    assert audit.calls[-1][1]["action"] == "delete"
    assert task.id not in repo.rows


def test_list_passes_filters_to_repository() -> None:
    service, repo, _, _ = _make_service()

    service.list_tasks(FARM, status="pendiente", priority=None, assigned_to=USER)

    assert repo.events == ["list:['assigned_to', 'status']"]


# ═══════════════════════════════════════════════════════════════
# 2. Repositorio (SQLite en memoria, tabla real)
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def sqlite_session() -> Iterator[Session]:
    engine = create_engine("sqlite://")
    Task.__table__.create(engine)
    with Session(engine) as session:
        yield session


def _task(farm_id: uuid.UUID, days: int, **overrides: Any) -> Task:
    values: dict[str, Any] = {
        "farm_id": farm_id,
        "assigned_to": USER,
        "assigned_by": USER,
        "title": f"tarea +{days}d",
        "task_type": "general",
        "due_date": DUE + timedelta(days=days),
    }
    values.update(overrides)
    return Task(**values)


def test_repository_never_returns_tasks_of_another_farm(sqlite_session: Session) -> None:
    repo = TaskRepository(sqlite_session)
    foreign = _task(OTHER_FARM, 0)
    repo.add(foreign)
    repo.commit()

    assert repo.get_in_farm(FARM, foreign.id) is None
    assert repo.get_in_farm(OTHER_FARM, foreign.id) is not None
    assert list(repo.list_by_farm(FARM)) == []


def test_repository_lists_most_urgent_first_and_filters(sqlite_session: Session) -> None:
    repo = TaskRepository(sqlite_session)
    for task in (_task(FARM, 5), _task(FARM, 1, priority="alta"), _task(FARM, 3, status="completada")):
        repo.add(task)
    repo.commit()

    titles = [t.title for t in repo.list_by_farm(FARM)]
    assert titles == ["tarea +1d", "tarea +3d", "tarea +5d"]
    assert [t.title for t in repo.list_by_farm(FARM, priority="alta")] == ["tarea +1d"]
    assert [t.title for t in repo.list_by_farm(FARM, status="completada")] == ["tarea +3d"]


# ═══════════════════════════════════════════════════════════════
# 3. Frontera HTTP (router + permisos + traducción de errores)
# ═══════════════════════════════════════════════════════════════


class _PermissionSession:
    """Sesión falsa que solo responde lo que consulta require_permission."""

    def __init__(self, allowed_actions: set[str]) -> None:
        self._allowed = allowed_actions

    def execute(self, stmt: Any) -> SimpleNamespace:
        entity = stmt.column_descriptions[0]["entity"].__name__
        if entity == "UserFarm":
            value: Any = SimpleNamespace(role_id=uuid.uuid4())
        else:  # Permission
            value = SimpleNamespace(**{a: a in self._allowed for a in ("can_create", "can_read", "can_update", "can_delete")})
        return SimpleNamespace(scalar_one_or_none=lambda: value)

    def get(self, model: Any, key: Any) -> SimpleNamespace:
        return SimpleNamespace(is_active=True)


@pytest.fixture
def http() -> Iterator[tuple[TestClient, FakeTaskRepository, set[str]]]:
    from app.core.database import get_db
    from app.modules.identity import get_current_user
    from app.main import app
    from app.modules.tasks.dependencies import get_task_service

    repo = FakeTaskRepository()
    allowed = {"can_create", "can_read", "can_update", "can_delete"}
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=USER)
    app.dependency_overrides[get_db] = lambda: _PermissionSession(allowed)
    app.dependency_overrides[get_task_service] = lambda: TaskService(repo, Recorder(), Recorder())  # type: ignore[arg-type]
    try:
        yield TestClient(app), repo, allowed
    finally:
        app.dependency_overrides.clear()


def _url(farm_id: uuid.UUID = FARM, task_id: uuid.UUID | None = None) -> str:
    base = f"/api/v1/farms/{farm_id}/tasks"
    return f"{base}/{task_id}" if task_id else base


def _payload() -> dict[str, str]:
    return {"assigned_to": str(uuid.uuid4()), "title": "Ordeño", "task_type": "produccion", "due_date": DUE.isoformat()}


def test_http_full_crud_contract(http: tuple[TestClient, FakeTaskRepository, set[str]]) -> None:
    client, _, _ = http

    created = client.post(_url(), json=_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["assigned_by"] == str(USER) and body["farm_id"] == str(FARM)
    task_id = body["id"]

    assert client.get(_url(task_id=uuid.UUID(task_id))).status_code == 200
    assert [t["id"] for t in client.get(_url()).json()] == [task_id]

    updated = client.put(_url(task_id=uuid.UUID(task_id)), json={"status": "en_progreso"})
    assert updated.status_code == 200 and updated.json()["status"] == "en_progreso"

    deleted = client.delete(_url(task_id=uuid.UUID(task_id)))
    assert deleted.status_code == 204 and deleted.content == b""


def test_http_missing_task_returns_404_with_original_message(http: tuple[TestClient, FakeTaskRepository, set[str]]) -> None:
    client, _, _ = http

    response = client.get(_url(task_id=uuid.uuid4()))

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarea no encontrada"}


def test_http_permission_is_enforced_per_action(http: tuple[TestClient, FakeTaskRepository, set[str]]) -> None:
    client, repo, allowed = http
    allowed.discard("can_create")

    response = client.post(_url(), json=_payload())

    assert response.status_code == 403
    assert response.json() == {"detail": "No tienes permiso para 'can_create' en 'tareas'"}
    assert repo.rows == {}


@pytest.mark.parametrize("entrypoint", ["app.main", "app.models", "app.modules.tasks"])
def test_app_boots_like_uvicorn(entrypoint: str) -> None:
    """Importa cada punto de entrada en un proceso limpio, como uvicorn o Alembic.

    Las demás pruebas comparten un proceso donde los módulos ya están cargados,
    así que no detectan ciclos de importación que dependen del orden. Esta sí.
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", f"import {entrypoint}; import app.main; print(len(app.main.app.routes))"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr[-1500:]


def test_http_invalid_body_returns_422(http: tuple[TestClient, FakeTaskRepository, set[str]]) -> None:
    client, _, _ = http

    response = client.post(_url(), json={"title": "sin responsable"})

    assert response.status_code == 422
