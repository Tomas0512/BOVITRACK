"""
Módulo: modules/tasks/service.py
¿Qué? Reglas de negocio de las tareas operativas: crear, listar, consultar,
      actualizar y eliminar tareas de una finca.
¿Para qué? Coordinar el trabajo diario del equipo: quién asigna, quién ejecuta
           y en qué estado está cada tarea.
¿Impacto? Esta capa no conoce HTTP ni SQLAlchemy:
          - los datos los pide al repositorio;
          - los errores los expresa con app.shared.exceptions (el router los
            traduce a 404, 400, etc.);
          - lo que pertenece a otros dominios (¿el bovino es de esta finca?,
            dejar rastro en la auditoría) lo recibe como colaborador inyectado.
            Así el módulo no se acopla a cómo están hechos esos otros dominios.
"""

import uuid
from collections.abc import Sequence

from app.modules.tasks.models import Task
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import TaskCreate, TaskUpdate
from app.shared.exceptions import NotFoundError
from app.shared.ports import AuditRecorder, FarmScopeChecker

TASK_NOT_FOUND = "Tarea no encontrada"


class TaskService:
    """Casos de uso del módulo de tareas."""

    def __init__(
        self,
        repository: TaskRepository,
        ensure_farm_scope: FarmScopeChecker,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._ensure_farm_scope = ensure_farm_scope
        self._record_audit = record_audit

    def create(self, farm_id: uuid.UUID, data: TaskCreate, assigned_by: uuid.UUID) -> Task:
        """Crea una tarea. assigned_by es el usuario autenticado que la asigna.

        Garantiza: bovino, lote y responsable pertenecen a la finca (si no, el
        colaborador de alcance rechaza la operación antes de guardar).
        """
        self._ensure_farm_scope(
            farm_id,
            bovine_id=data.bovine_id,
            land_plot_id=data.land_plot_id,
            member_user_id=data.assigned_to,
        )
        task = Task(farm_id=farm_id, assigned_by=assigned_by, **data.model_dump())
        self._repo.add(task)
        self._repo.commit()
        self._repo.refresh(task)
        self._record_audit(
            user_id=str(assigned_by),
            farm_id=str(farm_id),
            action="create",
            entity="task",
            entity_id=str(task.id),
            details={"title": task.title},
        )
        self._repo.commit()
        return task

    def list_tasks(
        self,
        farm_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
        assigned_to: uuid.UUID | None = None,
    ) -> Sequence[Task]:
        """Lista las tareas de la finca con filtros opcionales, las más urgentes primero."""
        return self._repo.list_by_farm(
            farm_id, status=status, priority=priority, assigned_to=assigned_to
        )

    def get(self, farm_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        """Devuelve la tarea. Lanza NotFoundError si no existe o es de otra finca."""
        task = self._repo.get_in_farm(farm_id, task_id)
        if task is None:
            raise NotFoundError(TASK_NOT_FOUND)
        return task

    def update(
        self,
        farm_id: uuid.UUID,
        task_id: uuid.UUID,
        data: TaskUpdate,
        user_id: uuid.UUID | None = None,
    ) -> Task:
        """Actualiza solo los campos enviados (estado, prioridad, observaciones…).

        Garantiza, igual que al crear, que un bovino o lote nuevo sea de esta finca
        (antes la edición no lo validaba: se podía apuntar a datos de otra finca).
        """
        task = self.get(farm_id, task_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("bovine_id") is not None or changes.get("land_plot_id") is not None:
            self._ensure_farm_scope(
                farm_id,
                bovine_id=changes.get("bovine_id"),
                land_plot_id=changes.get("land_plot_id"),
            )
        for field, value in changes.items():
            setattr(task, field, value)
        self._repo.commit()
        self._repo.refresh(task)
        self._record_audit(
            user_id=str(user_id) if user_id else None,
            farm_id=str(farm_id),
            action="update",
            entity="task",
            entity_id=str(task.id),
            details={"title": task.title, "status": task.status},
        )
        self._repo.commit()
        return task

    def delete(
        self,
        farm_id: uuid.UUID,
        task_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """Elimina la tarea de forma permanente, dejando constancia en la auditoría."""
        task = self.get(farm_id, task_id)
        self._record_audit(
            user_id=str(user_id) if user_id else None,
            farm_id=str(farm_id),
            action="delete",
            entity="task",
            entity_id=str(task.id),
            details={"title": task.title},
        )
        self._repo.delete(task)
        self._repo.commit()
