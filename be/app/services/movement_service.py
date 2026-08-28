import uuid
from datetime import date
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.movement import AnimalMovement, MOVEMENT_TYPES
from app.schemas.movement import MovementCreate, MovementUpdate
from app.services.audit_service import add_audit_log

_STATUS_MAP = {
    "compra": "activo",
    "venta": "vendido",
    "traslado": "activo",
    "nacimiento": "activo",
    "muerte": "muerto",
}

_TERMINAL_TYPES = {"venta", "muerte"}


def _apply_movement_to_bovine(db: Session, farm_id: uuid.UUID, movement: AnimalMovement) -> None:
    """¿Qué? Aplica el efecto (estado/salida) de un movimiento sobre su bovino.

    ¿Para qué? Unificar la lógica de cambio de estado para crear, actualizar y
               eliminar movimientos sin desincronizar el bovino.
    ¿Impacto? vendedo/muerto marcan el animal como inactivo y con fecha de salida.
    """
    if not movement.bovine_id or movement.movement_type not in _STATUS_MAP:
        return
    bovine = db.execute(
        select(Bovine).where(Bovine.id == movement.bovine_id, Bovine.farm_id == farm_id)
    ).scalar_one_or_none()
    if not bovine:
        return
    new_status = _STATUS_MAP[movement.movement_type]
    bovine.status = new_status
    bovine.is_active = new_status == "activo"
    if movement.movement_type in _TERMINAL_TYPES:
        bovine.exit_date = movement.movement_date
        bovine.exit_reason = movement.movement_type
    else:
        bovine.exit_date = None
        bovine.exit_reason = None


def _reconcile_bovine_status(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID | None) -> None:
    """¿Qué? Recalcula el estado del bovino según su movimiento más reciente.

    ¿Para qué? Después de actualizar o borrar un movimiento, el estado del
               bovino debe reflejar el último movimiento vigente (o volver a
               activo si no queda ninguno).
    """
    if not bovine_id:
        return
    latest = db.execute(
        select(AnimalMovement)
        .where(AnimalMovement.bovine_id == bovine_id, AnimalMovement.farm_id == farm_id)
        .order_by(AnimalMovement.movement_date.desc(), AnimalMovement.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    bovine = db.execute(select(Bovine).where(Bovine.id == bovine_id)).scalar_one_or_none()
    if not bovine:
        return
    if latest and latest.movement_type in _STATUS_MAP:
        _apply_movement_to_bovine(db, farm_id, latest)
        return
    bovine.status = "activo"
    bovine.is_active = True
    bovine.exit_date = None
    bovine.exit_reason = None


def create_movement(db: Session, farm_id: uuid.UUID, data: MovementCreate, user_id: uuid.UUID) -> AnimalMovement:
    if data.bovine_id:
        stmt = select(Bovine).where(Bovine.id == data.bovine_id, Bovine.farm_id == farm_id)
        bovine = db.execute(stmt).scalar_one_or_none()
        if not bovine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bovino no encontrado en esta finca")
        # ¿Qué? Evitar registrar un movimiento duplicado del mismo tipo/fecha.
        duplicate = db.execute(
            select(AnimalMovement.id).where(
                AnimalMovement.bovine_id == data.bovine_id,
                AnimalMovement.movement_type == data.movement_type,
                AnimalMovement.movement_date == data.movement_date,
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un movimiento de este tipo para el bovino en esa fecha",
            )

    movement = AnimalMovement(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(movement)

    if data.bovine_id:
        _apply_movement_to_bovine(db, farm_id, movement)

    db.commit()
    db.refresh(movement)
    add_audit_log(
        db, user_id=str(user_id), farm_id=str(farm_id),
        action="create", entity="movement", entity_id=str(movement.id),
        details={"type": data.movement_type, "bovine_id": str(data.bovine_id) if data.bovine_id else None},
    )
    db.commit()
    return movement


def list_movements(
    db: Session, farm_id: uuid.UUID,
    *,
    bovine_id: uuid.UUID | None = None,
    movement_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Sequence[AnimalMovement]:
    stmt = select(AnimalMovement).where(AnimalMovement.farm_id == farm_id)
    if bovine_id:
        stmt = stmt.where(AnimalMovement.bovine_id == bovine_id)
    if movement_type:
        stmt = stmt.where(AnimalMovement.movement_type == movement_type)
    if date_from:
        stmt = stmt.where(AnimalMovement.movement_date >= date_from)
    if date_to:
        stmt = stmt.where(AnimalMovement.movement_date <= date_to)
    stmt = stmt.order_by(AnimalMovement.movement_date.desc(), AnimalMovement.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_movement(db: Session, farm_id: uuid.UUID, movement_id: uuid.UUID) -> AnimalMovement:
    stmt = select(AnimalMovement).where(AnimalMovement.id == movement_id, AnimalMovement.farm_id == farm_id)
    movement = db.execute(stmt).scalar_one_or_none()
    if not movement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    return movement


def update_movement(db: Session, farm_id: uuid.UUID, movement_id: uuid.UUID, data: MovementUpdate, user_id: uuid.UUID | None = None) -> AnimalMovement:
    movement = get_movement(db, farm_id, movement_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(movement, field, value)
    # ¿Qué? Sincronizar el estado del bovino tras cambiar tipo/fecha del movimiento.
    _reconcile_bovine_status(db, farm_id, movement.bovine_id)
    db.commit()
    db.refresh(movement)
    add_audit_log(
        db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id),
        action="update", entity="movement", entity_id=str(movement.id),
    )
    db.commit()
    return movement


def delete_movement(db: Session, farm_id: uuid.UUID, movement_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    movement = get_movement(db, farm_id, movement_id)
    bovine_id = movement.bovine_id
    db.delete(movement)
    add_audit_log(
        db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id),
        action="delete", entity="movement", entity_id=str(movement.id),
    )
    # ¿Qué? Revertir el estado del bovino a su último movimiento vigente.
    _reconcile_bovine_status(db, farm_id, bovine_id)
    db.commit()
