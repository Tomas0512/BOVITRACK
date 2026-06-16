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


def create_movement(db: Session, farm_id: uuid.UUID, data: MovementCreate, user_id: uuid.UUID) -> AnimalMovement:
    if data.bovine_id:
        stmt = select(Bovine).where(Bovine.id == data.bovine_id, Bovine.farm_id == farm_id)
        bovine = db.execute(stmt).scalar_one_or_none()
        if not bovine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bovino no encontrado en esta finca")

    movement = AnimalMovement(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(movement)

    if data.bovine_id and data.movement_type in _STATUS_MAP:
        bovine = db.execute(select(Bovine).where(Bovine.id == data.bovine_id)).scalar_one()
        new_status = _STATUS_MAP[data.movement_type]
        bovine.status = new_status
        bovine.is_active = new_status != "muerto"
        if data.movement_type == "venta":
            bovine.exit_date = data.movement_date
            bovine.exit_reason = "venta"
        elif data.movement_type == "muerte":
            bovine.exit_date = data.movement_date
            bovine.exit_reason = "muerte"

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
    db.delete(movement)
    add_audit_log(
        db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id),
        action="delete", entity="movement", entity_id=str(movement.id),
    )
    db.commit()
