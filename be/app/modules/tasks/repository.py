"""
Módulo: modules/tasks/repository.py
¿Qué? Acceso a datos de la tabla `task`: buscar, listar, agregar, eliminar y
      confirmar la transacción.
¿Para qué? Que el servicio exprese *qué* necesita ("la tarea X de la finca Y")
           sin escribir consultas SQLAlchemy. Es la única capa del módulo que
           conoce la sesión de base de datos.
¿Impacto? Toda consulta filtra por farm_id: una tarea de otra finca simplemente
          "no existe" para quien pregunta desde esta finca.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tasks.models import Task


class TaskRepository:
    """Repositorio de tareas sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, task_id: uuid.UUID) -> Task | None:
        """Devuelve la tarea si existe y pertenece a la finca; si no, None."""
        stmt = select(Task).where(Task.id == task_id, Task.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        status: str | None = None,
        priority: str | None = None,
        assigned_to: uuid.UUID | None = None,
    ) -> Sequence[Task]:
        """Lista las tareas de la finca, las más urgentes primero (due_date asc)."""
        stmt = select(Task).where(Task.farm_id == farm_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if assigned_to:
            stmt = stmt.where(Task.assigned_to == assigned_to)
        stmt = stmt.order_by(Task.due_date.asc())
        return self._db.execute(stmt).scalars().all()

    def add(self, task: Task) -> None:
        """Agrega una tarea nueva a la unidad de trabajo (se guarda en commit)."""
        self._db.add(task)

    def delete(self, task: Task) -> None:
        """Marca la tarea para eliminarse (se borra en commit)."""
        self._db.delete(task)

    def commit(self) -> None:
        """Confirma la transacción en curso."""
        self._db.commit()

    def refresh(self, task: Task) -> None:
        """Recarga la tarea desde la BD (id, created_at y updated_at generados)."""
        self._db.refresh(task)
