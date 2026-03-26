"""
Módulo: routers/tasks.py
¿Qué? Router de FastAPI para el CRUD de tareas operativas.
¿Para qué? Permitir asignar, listar, actualizar y eliminar tareas
           entre los miembros de la finca.
¿Impacto? Las tareas coordinan el trabajo diario del equipo ganadero.
          La vista v_pending_tasks consume estos datos para el dashboard.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/tasks", tags=["Tareas"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Crear tarea", dependencies=[Depends(require_permission("tareas", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Crea una nueva tarea asignada a un miembro de la finca.
    ¿Para qué? assigned_by se toma del usuario autenticado (quién crea la tarea).
    ¿Impacto? Retorna 201 Created con la tarea completa.
    """
    task = task_service.create_task(db, farm_id, data, current_user.id)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse], summary="Listar tareas", dependencies=[Depends(require_permission("tareas", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    assigned_to: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    """¿Qué? Lista las tareas con filtros opcionales por query string.
    ¿Para qué? Filtrar por estado (pendiente/en_progreso/completada),
               prioridad (alta/media/baja) o responsable asignado.
    ¿Impacto? Ordenadas por fecha límite ascendente (las más urgentes primero).
    """
    _ = current_user
    tasks = task_service.list_tasks(db, farm_id, status_filter=status_filter, priority=priority, assigned_to=assigned_to)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse, summary="Obtener tarea por ID", dependencies=[Depends(require_permission("tareas", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Retorna el detalle de una tarea específica.
    ¿Para qué? Ver descripción completa, observaciones y estado.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    task = task_service.get_task(db, farm_id, task_id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse, summary="Actualizar tarea", dependencies=[Depends(require_permission("tareas", "can_update"))])
def update(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Actualiza parcialmente una tarea (solo los campos enviados).
    ¿Para qué? Cambiar estado, prioridad, agregar observaciones.
    ¿Impacto? Para marcar como completada, enviar status='completada' + completed_at.
    """
    _ = current_user
    task = task_service.update_task(db, farm_id, task_id, data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tarea", dependencies=[Depends(require_permission("tareas", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina una tarea de la base de datos.
    ¿Para qué? Remover tareas creadas por error.
    ¿Impacto? Eliminación permanente. Retorna 204 No Content.
    """
    _ = current_user
    task_service.delete_task(db, farm_id, task_id)
