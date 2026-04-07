"""
Módulo: routers/employees.py
¿Qué? Router de FastAPI para la gestión de empleados de una finca.
¿Para qué? Asignar, listar, actualizar y desvincular usuarios como empleados.
¿Impacto? Los permisos se controlan con el módulo 'usuarios' del sistema RBAC.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission
from app.schemas.employee import EmployeeResponse, EmployeeUpdate, RoleOption
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.services import employee_service
from app.services import invitation_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}", tags=["Empleados"])


@router.get(
    "/roles",
    response_model=list[RoleOption],
    summary="Listar roles disponibles",
    dependencies=[Depends(require_permission("usuarios", "can_read"))],
)
def list_roles(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RoleOption]:
    """¿Qué? Retorna todos los roles activos del sistema.
    ¿Para qué? Poblar el select de roles en el formulario de asignación de empleados.
    """
    _ = farm_id, current_user
    roles = employee_service.list_roles(db)
    return [RoleOption.model_validate(r) for r in roles]


@router.post(
    "/employees/invite",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invitar empleado a la finca",
    dependencies=[Depends(require_permission("usuarios", "can_create"))],
)
async def invite(
    farm_id: uuid.UUID,
    data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvitationResponse:
    """Envía una invitación por email para que un empleado se registre en la finca."""
    return await invitation_service.create_invitation(db, farm_id, data, current_user.id)


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
    summary="Listar empleados de la finca",
    dependencies=[Depends(require_permission("usuarios", "can_read"))],
)
def list_all(
    farm_id: uuid.UUID,
    is_active: bool | None = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EmployeeResponse]:
    """¿Qué? Lista todos los empleados de la finca con filtro opcional de estado.
    ¿Para qué? Ver empleados activos e inactivos por separado.
    ¿Impacto? Sin filtro retorna todos. Con ?is_active=true solo los activos.
    """
    _ = current_user
    return employee_service.list_employees(db, farm_id, is_active=is_active)


@router.put(
    "/employees/{user_id}",
    response_model=EmployeeResponse,
    summary="Actualizar empleado",
    dependencies=[Depends(require_permission("usuarios", "can_update"))],
)
def update(
    farm_id: uuid.UUID,
    user_id: uuid.UUID,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmployeeResponse:
    """¿Qué? Actualiza el rol o estado activo de un empleado en la finca.
    ¿Para qué? Cambiar de rol o activar/desactivar sin perder el historial.
    ¿Impacto? Retorna 404 si el usuario no está asignado a la finca.
    """
    _ = current_user
    return employee_service.update_employee(db, farm_id, user_id, data)


@router.delete(
    "/employees/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular empleado de la finca",
    dependencies=[Depends(require_permission("usuarios", "can_delete"))],
)
def remove(
    farm_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina la asignación de un usuario en la finca.
    ¿Para qué? Desvincular permanentemente a un empleado.
    ¿Impacto? Irreversible. Para desactivar temporalmente usar PUT con is_active=false.
    """
    _ = current_user
    employee_service.remove_employee(db, farm_id, user_id)
