"""
Módulo: services/task_service.py
¿Qué? Capa de servicio para el módulo de tareas operativas.
¿Para qué? Gestionar la asignación, seguimiento y cierre de tareas
           entre los miembros de la finca.
¿Impacto? Las tareas permiten coordinar el trabajo diario del equipo.
          La vista v_pending_tasks depende de estos datos.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, farm_id: uuid.UUID, data: TaskCreate, assigned_by: uuid.UUID) -> Task:
    """¿Qué? Crea una nueva tarea asignada a un miembro de la finca.
    ¿Para qué? Registrar quién asigna (assigned_by) y quién ejecuta (assigned_to).
    ¿Impacto? assigned_by se toma automáticamente del usuario autenticado.
    """
    task = Task(
        farm_id=farm_id,
        assigned_by=assigned_by,
        **data.model_dump(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    farm_id: uuid.UUID,
    *,
    status_filter: str | None = None,
    priority: str | None = None,
    assigned_to: uuid.UUID | None = None,
) -> Sequence[Task]:
    """¿Qué? Lista las tareas de una finca con filtros opcionales.
    ¿Para qué? Filtrar por estado (pendiente/en_progreso/completada),
               prioridad (alta/media/baja) o responsable.
    ¿Impacto? Ordenadas por fecha límite ascendente (las más urgentes primero).
    """
    stmt = select(Task).where(Task.farm_id == farm_id)
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if assigned_to:
        stmt = stmt.where(Task.assigned_to == assigned_to)
    stmt = stmt.order_by(Task.due_date.asc())
    return db.execute(stmt).scalars().all()


def get_task(db: Session, farm_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    """¿Qué? Obtiene una tarea por ID dentro de una finca.
    ¿Para qué? Consultar detalle o validar existencia antes de operar.
    ¿Impacto? Filtra por farm_id para seguridad entre fincas.
    """
    stmt = select(Task).where(Task.id == task_id, Task.farm_id == farm_id)
    task = db.execute(stmt).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return task


def update_task(db: Session, farm_id: uuid.UUID, task_id: uuid.UUID, data: TaskUpdate) -> Task:
    """¿Qué? Actualiza los campos enviados de una tarea.
    ¿Para qué? Cambiar estado, prioridad, agregar observaciones o marcar como completada.
    ¿Impacto? Al cambiar status a 'completada', el frontend debería enviar completed_at.
    """
    task = get_task(db, farm_id, task_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, farm_id: uuid.UUID, task_id: uuid.UUID) -> None:
    """¿Qué? Elimina una tarea de la base de datos.
    ¿Para qué? Remover tareas creadas por error o ya irrelevantes.
    ¿Impacto? Eliminación permanente. Las tareas completadas deberían
              archivarse, no eliminarse.
    """
    task = get_task(db, farm_id, task_id)
    db.delete(task)
    db.commit()
