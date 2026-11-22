"""
Módulo: modules/team/router/employees.py (frontera HTTP: empleados de una finca)
¿Qué? Roles, invitar, listar, actualizar, cerrar/abrir cuenta y desvincular
      empleados: /api/v1/farms/{farm_id}/...
¿Para qué? Traducir HTTP <-> casos de uso. Las reglas están en EmployeeService e
           InvitationService.
¿Impacto? Los permisos se controlan con el módulo 'usuarios' del sistema RBAC.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.team.dependencies import (
    get_current_user,
    get_employee_service,
    get_invitation_service,
    require_permission,
)
from app.modules.team.schemas import (
    AccountStatusUpdate,
    EmployeeResponse,
    EmployeeUpdate,
    InvitationCreate,
    InvitationResponse,
    RoleOption,
)
from app.modules.team.service import EmployeeService, InvitationService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}", tags=["Empleados"])


@router.get(
    "/roles",
    response_model=list[RoleOption],
    summary="Listar roles disponibles",
    dependencies=[Depends(require_permission("usuarios", "can_read"))],
)
def list_roles(
    farm_id: uuid.UUID,
    service: EmployeeService = Depends(get_employee_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[RoleOption]:
    """¿Qué? Retorna todos los roles activos del sistema.
    ¿Para qué? Poblar el select de roles en el formulario de asignación de empleados.
    """
    _ = farm_id, current_user
    return [RoleOption.model_validate(r) for r in service.roles()]


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
    service: InvitationService = Depends(get_invitation_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> InvitationResponse:
    """Envía una invitación por email para que un empleado se registre en la finca."""
    return await service.invite(farm_id, data, current_user.id)


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
    summary="Listar empleados de la finca",
    dependencies=[Depends(require_permission("usuarios", "can_read"))],
)
def list_all(
    farm_id: uuid.UUID,
    is_active: bool | None = Query(None, description="Filtrar por estado activo/inactivo"),
    service: EmployeeService = Depends(get_employee_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[EmployeeResponse]:
    """¿Qué? Lista todos los empleados de la finca con filtro opcional de estado.
    ¿Para qué? Ver empleados activos e inactivos por separado.
    ¿Impacto? Sin filtro retorna todos. Con ?is_active=true solo los activos.
    """
    _ = current_user
    return service.list(farm_id, is_active=is_active)


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
    service: EmployeeService = Depends(get_employee_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EmployeeResponse:
    """¿Qué? Actualiza el rol o estado activo de un empleado en la finca.
    ¿Para qué? Cambiar de rol o activar/desactivar sin perder el historial.
    ¿Impacto? Retorna 404 si el usuario no está asignado a la finca.
    """
    return service.update(farm_id, user_id, data, current_user.id)


@router.put(
    "/employees/{user_id}/account",
    response_model=EmployeeResponse,
    summary="Activar o desactivar la cuenta de un usuario",
    dependencies=[Depends(require_permission("usuarios", "can_delete"))],
)
def set_account_status(
    farm_id: uuid.UUID,
    user_id: uuid.UUID,
    data: AccountStatusUpdate,
    service: EmployeeService = Depends(get_employee_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EmployeeResponse:
    """¿Qué? Cierra o restablece el acceso al sistema de un usuario.

    COMO: administrador de la finca
    QUIERO: impedir que una persona vuelva a iniciar sesión
    PARA:   dar de baja a alguien que ya no trabaja en la organización.

    ¿Impacto? Esto NO es lo mismo que desactivar al empleado en la finca
              (`PUT /employees/{user_id}`), que solo le quita el acceso a esta
              finca. Cerrar la cuenta bloquea el login en TODAS sus fincas y
              anula sus sesiones abiertas. Por eso se reserva al rol
              Administrador, aunque el permiso RBAC ya lo restrinja hoy.
    """
    return service.set_account_status(farm_id, user_id, is_active=data.is_active, reason=data.reason,
                                      actor_id=current_user.id)


@router.delete(
    "/employees/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular empleado de la finca",
    dependencies=[Depends(require_permission("usuarios", "can_delete"))],
)
def remove(
    farm_id: uuid.UUID,
    user_id: uuid.UUID,
    service: EmployeeService = Depends(get_employee_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina la asignación de un usuario en la finca.
    ¿Para qué? Desvincular permanentemente a un empleado.
    ¿Impacto? Irreversible. Para desactivar temporalmente usar PUT con is_active=false.
    """
    service.remove(farm_id, user_id, current_user.id)
