"""
Módulo: modules/farms/router/land_plots.py (frontera HTTP: lotes)
¿Qué? CRUD de lotes dentro de una finca: /api/v1/farms/{farm_id}/land-plots.
¿Para qué? Gestionar los lotes que organizan el hato y la infraestructura.
¿Impacto? Protegido por RBAC módulo 'fincas'. Las reglas están en LandPlotService.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.farms.dependencies import get_current_user, get_land_plot_service, require_permission
from app.modules.farms.schemas import LandPlotCreate, LandPlotResponse, LandPlotUpdate
from app.modules.farms.service import LandPlotService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/land-plots", tags=["Lotes"])


@router.post(
    "",
    response_model=LandPlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear lote",
    dependencies=[Depends(require_permission("fincas", "can_create"))],
)
def create(
    farm_id: uuid.UUID,
    data: LandPlotCreate,
    service: LandPlotService = Depends(get_land_plot_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> LandPlotResponse:
    return LandPlotResponse.model_validate(service.create(farm_id, data, current_user.id))


@router.get(
    "",
    response_model=list[LandPlotResponse],
    summary="Listar lotes de la finca",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def list_all(
    farm_id: uuid.UUID,
    is_active: bool | None = Query(None),
    service: LandPlotService = Depends(get_land_plot_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[LandPlotResponse]:
    _ = current_user
    return [LandPlotResponse.model_validate(lp) for lp in service.list(farm_id, is_active=is_active)]


@router.get(
    "/{land_plot_id}",
    response_model=LandPlotResponse,
    summary="Obtener lote por ID",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def get_one(
    farm_id: uuid.UUID,
    land_plot_id: uuid.UUID,
    service: LandPlotService = Depends(get_land_plot_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> LandPlotResponse:
    _ = current_user
    return LandPlotResponse.model_validate(service.get(farm_id, land_plot_id))


@router.put(
    "/{land_plot_id}",
    response_model=LandPlotResponse,
    summary="Actualizar lote",
    dependencies=[Depends(require_permission("fincas", "can_update"))],
)
def update(
    farm_id: uuid.UUID,
    land_plot_id: uuid.UUID,
    data: LandPlotUpdate,
    service: LandPlotService = Depends(get_land_plot_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> LandPlotResponse:
    return LandPlotResponse.model_validate(service.update(farm_id, land_plot_id, data, current_user.id))


@router.delete(
    "/{land_plot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lote",
    dependencies=[Depends(require_permission("fincas", "can_delete"))],
)
def delete(
    farm_id: uuid.UUID,
    land_plot_id: uuid.UUID,
    service: LandPlotService = Depends(get_land_plot_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    service.deactivate(farm_id, land_plot_id, current_user.id)
