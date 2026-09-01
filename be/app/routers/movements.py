import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.movement import MovementCreate, MovementResponse, MovementUpdate
from app.services import movement_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/movements", tags=["Movimientos"])


@router.post("", response_model=MovementResponse, status_code=status.HTTP_201_CREATED, summary="Registrar movimiento", dependencies=[Depends(require_permission("bovinos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovementResponse:
    movement = movement_service.create_movement(db, farm_id, data, current_user.id)
    return MovementResponse.model_validate(movement)


@router.get("", response_model=list[MovementResponse], summary="Listar movimientos", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    movement_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MovementResponse]:
    _ = current_user
    movements = movement_service.list_movements(db, farm_id, bovine_id=bovine_id, movement_type=movement_type, date_from=date_from, date_to=date_to)
    return [MovementResponse.model_validate(m) for m in movements]


@router.get("/{movement_id}", response_model=MovementResponse, summary="Obtener movimiento", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovementResponse:
    _ = current_user
    movement = movement_service.get_movement(db, farm_id, movement_id)
    return MovementResponse.model_validate(movement)


@router.put("/{movement_id}", response_model=MovementResponse, summary="Actualizar movimiento", dependencies=[Depends(require_permission("bovinos", "can_update"))])
def update(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    data: MovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovementResponse:
    _ = current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Los movimientos del hato son registros inmutables y no se pueden editar",
    )


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar movimiento", dependencies=[Depends(require_permission("bovinos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    movement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _ = current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Los movimientos del hato son registros inmutables y no se pueden eliminar",
    )
