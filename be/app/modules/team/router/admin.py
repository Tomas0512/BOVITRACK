"""
Módulo: modules/team/router/admin.py (frontera HTTP: moderación de reactivaciones)
¿Qué? /api/v1/admin/reactivation-requests: listar, aprobar y rechazar solicitudes.
¿Para qué? Que un Administrador recupere el acceso de alguien de sus fincas.
¿Impacto? El guard require_admin_role exige ser Administrador de alguna finca (403),
          y el servicio limita el alcance a las personas de SUS fincas (404 fuera de él).
"""

import uuid

from fastapi import APIRouter, Depends

from app.modules.team.dependencies import get_reactivation_service, require_admin_role
from app.modules.team.schemas import ReactivationRequestDetail, ReactivationRequestResponse
from app.modules.team.service import ReactivationService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])


@router.get(
    "/reactivation-requests",
    response_model=list[ReactivationRequestDetail],
    summary="Listar solicitudes de reactivación pendientes",
)
def list_pending(
    service: ReactivationService = Depends(get_reactivation_service),
    current_user: CurrentUser = Depends(require_admin_role),
) -> list[ReactivationRequestDetail]:
    return service.list_pending(current_user.id)


@router.post(
    "/reactivation-requests/{request_id}/approve",
    response_model=ReactivationRequestResponse,
    summary="Aprobar solicitud de reactivación",
)
def approve(
    request_id: uuid.UUID,
    service: ReactivationService = Depends(get_reactivation_service),
    current_user: CurrentUser = Depends(require_admin_role),
) -> ReactivationRequestResponse:
    return ReactivationRequestResponse.model_validate(service.approve(request_id, current_user.id))


@router.post(
    "/reactivation-requests/{request_id}/reject",
    response_model=ReactivationRequestResponse,
    summary="Rechazar solicitud de reactivación",
)
def reject(
    request_id: uuid.UUID,
    service: ReactivationService = Depends(get_reactivation_service),
    current_user: CurrentUser = Depends(require_admin_role),
) -> ReactivationRequestResponse:
    return ReactivationRequestResponse.model_validate(service.reject(request_id, current_user.id))
