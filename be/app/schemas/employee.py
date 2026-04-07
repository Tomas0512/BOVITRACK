"""
Módulo: schemas/employee.py
¿Qué? Schemas Pydantic para el módulo de empleados (asignación de usuarios a fincas).
¿Para qué? Validar los datos de entrada y salida al gestionar empleados de una finca.
¿Impacto? Sin estos schemas, se podrían asignar usuarios sin rol o con datos inválidos.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RoleOption(BaseModel):
    """¿Qué? Opción de rol para selects en formularios.
    ¿Para qué? Mostrar los roles disponibles al asignar un empleado.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None


class EmployeeAssign(BaseModel):
    """¿Qué? Datos requeridos para asignar un usuario como empleado a una finca.
    ¿Para qué? Busca al usuario por email y le asigna un rol en la finca.
    ¿Impacto? Si el usuario ya está asignado a la finca, se retorna 409 Conflict.
    """

    user_email: EmailStr
    role_id: uuid.UUID


class EmployeeUpdate(BaseModel):
    """¿Qué? Datos para actualizar la asignación de un empleado en la finca.
    ¿Para qué? Cambiar el rol o activar/desactivar al empleado.
    ¿Impacto? Todos los campos son opcionales — solo se actualizan los enviados.
    """

    role_id: uuid.UUID | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    """¿Qué? Schema de respuesta con datos combinados de UserFarm + User + Role.
    ¿Para qué? Mostrar en la UI el nombre, email, rol y estado del empleado.
    ¿Impacto? Se construye manualmente desde el servicio (no es from_attributes directo).
    """

    id: uuid.UUID
    user_id: uuid.UUID
    farm_id: uuid.UUID
    role_id: uuid.UUID
    role_name: str
    is_active: bool
    assigned_at: datetime
    first_name: str
    last_name: str
    email: str
    document_type: str
    document_number: str
    phone: str | None = None
