"""
Módulo: modules/health/router.py (frontera HTTP del módulo: tratamientos y planes sanitarios)
¿Qué? Router de FastAPI para el CRUD de tratamientos sanitarios.
¿Para qué? Permitir registrar vacunaciones, desparasitaciones y
           tratamientos veterinarios asociados a bovinos o potreros.
¿Impacto? La trazabilidad sanitaria es obligatoria para el ICA.
          Cada endpoint requiere autenticación JWT.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status


from app.modules.health.dependencies import (
    get_current_user,
    get_sanitary_plan_service,
    get_treatment_service,
    require_permission,
)

from app.modules.health.schemas import (
    SanitaryPlanCreate,
    SanitaryPlanResponse,
    SanitaryPlanUpdate,
    TreatmentCreate,
    TreatmentResponse,
)
from app.modules.health.service import SanitaryPlanService, TreatmentService
from app.shared.ports import CurrentUser

treatments_router = APIRouter(prefix="/api/v1/farms/{farm_id}/treatments", tags=["Tratamientos"])


@treatments_router.post("", response_model=TreatmentResponse, status_code=status.HTTP_201_CREATED, summary="Registrar tratamiento", dependencies=[Depends(require_permission("tratamientos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: TreatmentCreate,
    service: TreatmentService = Depends(get_treatment_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> TreatmentResponse:
    """¿Qué? Registra un tratamiento sanitario en la finca.
    ¿Para qué? Vincular el tratamiento al usuario que lo aplicó (applied_by).
    ¿Impacto? Retorna 201 Created con el tratamiento completo.
    """
    treatment = service.create_treatment(farm_id, data, current_user.id)
    return TreatmentResponse.model_validate(treatment)


@treatments_router.get("", response_model=list[TreatmentResponse], summary="Listar tratamientos", dependencies=[Depends(require_permission("tratamientos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    service: TreatmentService = Depends(get_treatment_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[TreatmentResponse]:
    """¿Qué? Lista tratamientos de la finca con filtro opcional por bovino.
    ¿Para qué? Consultar historial sanitario completo o de un animal específico.
    ¿Impacto? bovine_id como query parameter permite filtrar desde el frontend.
    """
    _ = current_user
    treatments = service.list_treatments(farm_id, bovine_id)
    return [TreatmentResponse.model_validate(t) for t in treatments]


@treatments_router.get("/{treatment_id}", response_model=TreatmentResponse, summary="Obtener tratamiento por ID", dependencies=[Depends(require_permission("tratamientos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    treatment_id: uuid.UUID,
    service: TreatmentService = Depends(get_treatment_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> TreatmentResponse:
    """¿Qué? Retorna el detalle de un tratamiento específico.
    ¿Para qué? Ver dosis, vía, diagnóstico y observaciones del tratamiento.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    treatment = service.get_treatment(farm_id, treatment_id)
    return TreatmentResponse.model_validate(treatment)


@treatments_router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tratamiento", dependencies=[Depends(require_permission("tratamientos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    treatment_id: uuid.UUID,
    service: TreatmentService = Depends(get_treatment_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina permanentemente un tratamiento registrado por error.
    ¿Para qué? Corrección de datos. No es soft delete porque no tiene dependencias.
    ¿Impacto? Retorna 204 No Content. La eliminación es irreversible.
    """
    _ = current_user
    service.delete_treatment(farm_id, treatment_id, current_user.id)


# ═══ Planes sanitarios ═══════════════════════════════════════════

sanitary_router = APIRouter(prefix="/api/v1/farms/{farm_id}/sanitary-plans", tags=["Planes Sanitarios"])


@sanitary_router.post("", response_model=SanitaryPlanResponse, status_code=status.HTTP_201_CREATED, summary="Crear plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_create"))], name="create")
def create_plan(
    farm_id: uuid.UUID,
    data: SanitaryPlanCreate,
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = service.create_sanitary_plan(farm_id, data, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@sanitary_router.get("", response_model=list[SanitaryPlanResponse], summary="Listar planes sanitarios", dependencies=[Depends(require_permission("sanitario", "can_read"))], name="list_all")
def list_plans(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    land_plot_id: uuid.UUID | None = Query(None),
    include_inactive: bool = Query(False),
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[SanitaryPlanResponse]:
    _ = current_user
    plans = service.list_sanitary_plans(farm_id, bovine_id, land_plot_id, include_inactive)
    return [SanitaryPlanResponse.model_validate(p) for p in plans]


@sanitary_router.get("/{plan_id}", response_model=SanitaryPlanResponse, summary="Obtener plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_read"))], name="get_one")
def get_plan(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> SanitaryPlanResponse:
    _ = current_user
    plan = service.get_sanitary_plan(farm_id, plan_id)
    return SanitaryPlanResponse.model_validate(plan)


@sanitary_router.put("/{plan_id}", response_model=SanitaryPlanResponse, summary="Actualizar plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_update"))])
def update(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    data: SanitaryPlanUpdate,
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = service.update_sanitary_plan(farm_id, plan_id, data, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@sanitary_router.post("/{plan_id}/apply", response_model=SanitaryPlanResponse, summary="Marcar plan como aplicado", dependencies=[Depends(require_permission("sanitario", "can_update"))])
def mark_applied(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> SanitaryPlanResponse:
    plan = service.mark_as_applied(farm_id, plan_id, current_user.id)
    return SanitaryPlanResponse.model_validate(plan)


@sanitary_router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar plan sanitario", dependencies=[Depends(require_permission("sanitario", "can_delete"))], name="delete")
def delete_plan(
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    service: SanitaryPlanService = Depends(get_sanitary_plan_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    _ = current_user
    service.deactivate_sanitary_plan(farm_id, plan_id, current_user.id)


# Router del módulo: incluye los dos agregados de salud (tratamientos y planes).
router = APIRouter()
router.include_router(treatments_router)
router.include_router(sanitary_router)
