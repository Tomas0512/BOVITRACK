"""
Módulo: modules/tasks/router.py (frontera HTTP del módulo)
¿Qué? Endpoints REST para asignar, listar, consultar, actualizar y eliminar
      tareas de una finca: /api/v1/farms/{farm_id}/tasks.
¿Para qué? Traducir HTTP <-> casos de uso: valida la entrada con los schemas,
           exige el permiso del módulo "tareas", llama a TaskService y
           convierte el resultado en TaskResponse.
¿Impacto? Aquí no hay reglas de negocio ni consultas. Los errores de dominio
          (p. ej. NotFoundError) los traduce app.core.error_handlers (404).
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.tasks.dependencies import get_current_user, get_task_service, require_permission
from app.modules.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.modules.tasks.service import TaskService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/tasks", tags=["Tareas"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Crear tarea", dependencies=[Depends(require_permission("tareas", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Crea una nueva tarea asignada a un miembro de la finca.
    ¿Para qué? assigned_by se toma del usuario autenticado (quién crea la tarea).
    ¿Impacto? Retorna 201 Created con la tarea completa.
    """
    task = service.create(farm_id, data, current_user.id)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse], summary="Listar tareas", dependencies=[Depends(require_permission("tareas", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    assigned_to: uuid.UUID | None = Query(None),
    service: TaskService = Depends(get_task_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[TaskResponse]:
    """¿Qué? Lista las tareas con filtros opcionales por query string.
    ¿Para qué? Filtrar por estado (pendiente/en_progreso/completada),
               prioridad (alta/media/baja) o responsable asignado.
    ¿Impacto? Ordenadas por fecha límite ascendente (las más urgentes primero).
    """
    _ = current_user
    tasks = service.list_tasks(farm_id, status=status_filter, priority=priority, assigned_to=assigned_to)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse, summary="Obtener tarea por ID", dependencies=[Depends(require_permission("tareas", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Retorna el detalle de una tarea específica.
    ¿Para qué? Ver descripción completa, observaciones y estado.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    return TaskResponse.model_validate(service.get(farm_id, task_id))


@router.put("/{task_id}", response_model=TaskResponse, summary="Actualizar tarea", dependencies=[Depends(require_permission("tareas", "can_update"))])
def update(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskResponse:
    """¿Qué? Actualiza parcialmente una tarea (solo los campos enviados).
    ¿Para qué? Cambiar estado, prioridad, agregar observaciones.
    ¿Impacto? Para marcar como completada, enviar status='completada' + completed_at.
    """
    task = service.update(farm_id, task_id, data, current_user.id)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tarea", dependencies=[Depends(require_permission("tareas", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina una tarea de la base de datos.
    ¿Para qué? Remover tareas creadas por error.
    ¿Impacto? Eliminación permanente. Retorna 204 No Content.
    """
    service.delete(farm_id, task_id, current_user.id)
