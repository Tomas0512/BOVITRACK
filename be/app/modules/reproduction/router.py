"""
Módulo: modules/reproduction/router.py (frontera HTTP del módulo)
¿Qué? Endpoints de /api/v1/farms/{farm_id}/reproductive-events: CRUD de eventos
      reproductivos, exigiendo el permiso del módulo "reproductivo".
¿Impacto? Sin reglas de negocio ni consultas. Los errores de dominio los
          traduce app.core.error_handlers (400 regla, 404 no encontrado).
"""

import uuid

from fastapi import APIRouter, Depends, Query, status


from app.modules.reproduction.schemas import ReproductiveEventCreate, ReproductiveEventResponse, ReproductiveEventUpdate
from app.modules.reproduction.dependencies import (
    get_current_user,
    get_reproduction_service,
    require_permission,
)

from app.modules.reproduction.service import ReproductionService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/reproductive-events", tags=["Eventos Reproductivos"])


@router.post("", response_model=ReproductiveEventResponse, status_code=status.HTTP_201_CREATED, summary="Registrar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: ReproductiveEventCreate,
    service: ReproductionService = Depends(get_reproduction_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ReproductiveEventResponse:
    event = service.create_event(farm_id, data, current_user.id)
    return ReproductiveEventResponse.model_validate(event)


@router.get("", response_model=list[ReproductiveEventResponse], summary="Listar eventos reproductivos", dependencies=[Depends(require_permission("reproductivo", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    event_type: str | None = Query(None),
    service: ReproductionService = Depends(get_reproduction_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[ReproductiveEventResponse]:
    _ = current_user
    events = service.list_events(farm_id, bovine_id, event_type)
    return [ReproductiveEventResponse.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=ReproductiveEventResponse, summary="Obtener evento por ID", dependencies=[Depends(require_permission("reproductivo", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    service: ReproductionService = Depends(get_reproduction_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ReproductiveEventResponse:
    _ = current_user
    event = service.get_event(farm_id, event_id)
    return ReproductiveEventResponse.model_validate(event)


@router.put("/{event_id}", response_model=ReproductiveEventResponse, summary="Actualizar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_update"))])
def update(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    data: ReproductiveEventUpdate,
    service: ReproductionService = Depends(get_reproduction_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ReproductiveEventResponse:
    event = service.update_event(farm_id, event_id, data, current_user.id)
    return ReproductiveEventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    service: ReproductionService = Depends(get_reproduction_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    _ = current_user
    service.delete_event(farm_id, event_id, current_user.id)
