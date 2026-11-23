import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.modules.livestock.dependencies import get_current_user, get_movement_service, require_permission
from app.modules.livestock.schemas import MovementCreate, MovementResponse, MovementUpdate
from app.modules.livestock.service import MovementService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/movements", tags=["Movimientos"])


@router.post("", response_model=MovementResponse, status_code=status.HTTP_201_CREATED, summary="Registrar movimiento", dependencies=[Depends(require_permission("bovinos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: MovementCreate,
    service: MovementService = Depends(get_movement_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> MovementResponse:
    movement = service.create_movement(farm_id, data, current_user.id)
    return MovementResponse.model_validate(movement)


@router.get("", response_model=list[MovementResponse], summary="Listar movimientos", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    movement_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    service: MovementService = Depends(get_movement_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[MovementResponse]:
    _ = current_user
    movements = service.list_movements(farm_id, bovine_id=bovine_id, movement_type=movement_type, date_from=date_from, date_to=date_to)
    return [MovementResponse.model_validate(m) for m in movements]


@router.get("/{movement_id}", response_model=MovementResponse, summary="Obtener movimiento", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    service: MovementService = Depends(get_movement_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> MovementResponse:
    _ = current_user
    movement = service.get_movement(farm_id, movement_id)
    return MovementResponse.model_validate(movement)


@router.put("/{movement_id}", response_model=MovementResponse, summary="Actualizar movimiento", dependencies=[Depends(require_permission("bovinos", "can_update"))])
def update(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    data: MovementUpdate,
    service: MovementService = Depends(get_movement_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> MovementResponse:
    _ = (current_user, data)
    # Regla de negocio (inmutabilidad) en el servicio -> PermissionDeniedError -> 403.
    service.update_movement(farm_id, movement_id)


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar movimiento", dependencies=[Depends(require_permission("bovinos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    service: MovementService = Depends(get_movement_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    _ = current_user
    service.delete_movement(farm_id, movement_id)
