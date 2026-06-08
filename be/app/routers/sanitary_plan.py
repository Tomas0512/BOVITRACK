"""
Módulo: routers/sanitary_plan.py
¿Qué? Router de FastAPI para el CRUD de planes sanitarios.
¿Para qué? Exponer endpoints REST para gestionar vacunas y tratamientos.
¿Impacto? Cada endpoint protegido por JWT + RBAC.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.sanitary_plan import SanitaryPlanCreate, SanitaryPlanResponse, SanitaryPlanUpdate
from app.services import sanitary_plan_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/sanitary-plans", tags=["Planes Sanitarios"])


@router.post("", response_model=SanitaryPlanResponse, status_code=status.HTTP_201_CREATED, summary="Crear plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: SanitaryPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = sanitary_plan_service.create_sanitary_plan(db, farm_id, data, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@router.get("", response_model=list[SanitaryPlanResponse], summary="Listar planes sanitarios", dependencies=[Depends(require_permission("sanitario", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    land_plot_id: uuid.UUID | None = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SanitaryPlanResponse]:
    _ = current_user
    plans = sanitary_plan_service.list_sanitary_plans(db, farm_id, bovine_id, land_plot_id, include_inactive)
    return [SanitaryPlanResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=SanitaryPlanResponse, summary="Obtener plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SanitaryPlanResponse:
    _ = current_user
    plan = sanitary_plan_service.get_sanitary_plan(db, farm_id, plan_id)
    return SanitaryPlanResponse.model_validate(plan)


@router.put("/{plan_id}", response_model=SanitaryPlanResponse, summary="Actualizar plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_update"))])
def update(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    data: SanitaryPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = sanitary_plan_service.update_sanitary_plan(db, farm_id, plan_id, data, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@router.post("/{plan_id}/apply", response_model=SanitaryPlanResponse, summary="Marcar plan como aplicado", dependencies=[Depends(require_permission("sanitario", "can_update"))])
def mark_applied(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = sanitary_plan_service.mark_as_applied(db, farm_id, plan_id, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _ = current_user
    sanitary_plan_service.deactivate_sanitary_plan(db, farm_id, plan_id, current_user.id)
