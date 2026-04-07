"""
Módulo: routers/land_plots.py
¿Qué? Router FastAPI para CRUD de lotes dentro de una finca.
¿Para qué? Gestionar los lotes que organizan el hato y la infraestructura.
¿Impacto? Protegido por RBAC módulo 'fincas'.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission
from app.schemas.land_plot import LandPlotCreate, LandPlotResponse, LandPlotUpdate
from app.services import land_plot_service

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LandPlotResponse:
    _ = current_user
    lp = land_plot_service.create_land_plot(db, farm_id, data)
    return LandPlotResponse.model_validate(lp)


@router.get(
    "",
    response_model=list[LandPlotResponse],
    summary="Listar lotes de la finca",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def list_all(
    farm_id: uuid.UUID,
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LandPlotResponse]:
    _ = current_user
    lps = land_plot_service.list_land_plots(db, farm_id, is_active=is_active)
    return [LandPlotResponse.model_validate(lp) for lp in lps]


@router.get(
    "/{land_plot_id}",
    response_model=LandPlotResponse,
    summary="Obtener lote por ID",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def get_one(
    farm_id: uuid.UUID,
    land_plot_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LandPlotResponse:
    _ = current_user
    lp = land_plot_service.get_land_plot(db, farm_id, land_plot_id)
    return LandPlotResponse.model_validate(lp)


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LandPlotResponse:
    _ = current_user
    lp = land_plot_service.update_land_plot(db, farm_id, land_plot_id, data)
    return LandPlotResponse.model_validate(lp)


@router.delete(
    "/{land_plot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lote",
    dependencies=[Depends(require_permission("fincas", "can_delete"))],
)
def delete(
    farm_id: uuid.UUID,
    land_plot_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _ = current_user
    land_plot_service.delete_land_plot(db, farm_id, land_plot_id)
