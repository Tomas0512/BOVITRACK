"""
Módulo: schemas/task.py
¿Qué? Schemas Pydantic para validar datos de tareas operativas.
¿Para qué? Gestionar la asignación y seguimiento de tareas entre
           miembros de la finca (capataz, veterinario, empleado).
¿Impacto? Sin estos schemas, se podrían asignar tareas sin título
          ni responsable, perdiendo trazabilidad operativa.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """¿Qué? Datos requeridos para crear una tarea.
    ¿Para qué? Asignar una tarea a un usuario con fecha límite y prioridad.
    ¿Impacto? assigned_to es obligatorio — toda tarea DEBE tener un responsable.
              El assigned_by se toma automáticamente del usuario autenticado.
    """

    assigned_to: uuid.UUID
    title: str
    description: str | None = None
    task_type: str
    due_date: datetime
    status: str = "pendiente"
    priority: str = "media"
    bovine_id: uuid.UUID | None = None
    land_plot_id: uuid.UUID | None = None
    observations: str | None = None


class TaskUpdate(BaseModel):
    """¿Qué? Schema para actualización parcial de una tarea.
    ¿Para qué? Permitir cambiar estado (pendiente → en_progreso → completada),
               prioridad, fecha límite o agregar observaciones.
    ¿Impacto? completed_at se establece cuando el estado cambia a 'completada'.
    """

    title: str | None = None
    description: str | None = None
    task_type: str | None = None
    due_date: datetime | None = None
    status: str | None = None
    priority: str | None = None
    bovine_id: uuid.UUID | None = None
    land_plot_id: uuid.UUID | None = None
    observations: str | None = None
    completed_at: datetime | None = None


class TaskResponse(BaseModel):
    """¿Qué? Schema de respuesta para una tarea.
    ¿Para qué? Incluye assigned_to y assigned_by para saber quién asignó y quién ejecuta.
    ¿Impacto? La vista v_pending_tasks consume estos mismos datos para reportes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    assigned_to: uuid.UUID
    assigned_by: uuid.UUID
    title: str
    description: str | None
    task_type: str
    due_date: datetime
    completed_at: datetime | None
    status: str
    priority: str
    bovine_id: uuid.UUID | None
    land_plot_id: uuid.UUID | None
    observations: str | None
    created_at: datetime
    updated_at: datetime
