import uuid
from datetime import timedelta
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.reproductive_event import ReproductiveEvent
from app.schemas.reproductive_event import ReproductiveEventCreate, ReproductiveEventUpdate
from app.services.audit_service import add_audit_log


GESTATION_DAYS = 283

_CALF_SEX_MAP: dict[str, list[str]] = {
    "macho": ["macho"],
    "hembra": ["hembra"],
    "gemelos": ["macho", "hembra"],
}


def create_event(db: Session, farm_id: uuid.UUID, data: ReproductiveEventCreate, user_id: uuid.UUID) -> ReproductiveEvent:
    if data.bovine_id:
        maternal = db.execute(
            select(Bovine).where(Bovine.id == data.bovine_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not maternal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El bovino indicado no existe en esta finca",
            )
        if data.event_type == "parto" and maternal.sex != "hembra":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo una hembra puede registrar un parto",
            )
    if data.bull_id:
        bull = db.execute(
            select(Bovine).where(Bovine.id == data.bull_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not bull:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El toro indicado no existe en esta finca",
            )
    if data.calf_id:
        calf = db.execute(
            select(Bovine).where(Bovine.id == data.calf_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not calf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cría indicada no existe en esta finca",
            )

    event = ReproductiveEvent(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    if event.event_type == "servicio" and event.due_date is None:
        event.due_date = event.event_date + timedelta(days=GESTATION_DAYS)

    if event.event_type == "parto":
        calves = _create_calves_from_birth(db, farm_id, event, user_id)
        if calves:
            event.calf_id = calves[0].id

    db.add(event)
    db.commit()
    db.refresh(event)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="reproductive_event", entity_id=str(event.id), details={"type": event.event_type})
    db.commit()
    return event


def _create_calves_from_birth(db: Session, farm_id: uuid.UUID, event: ReproductiveEvent, user_id: uuid.UUID) -> list[Bovine]:
    sexes = _CALF_SEX_MAP.get(event.result)
    if not sexes:
        return []

    prefix = str(event.bovine_id)[:6]
    date_str = event.event_date.strftime("%Y%m%d")
    calves: list[Bovine] = []

    for i, sex in enumerate(sexes):
        ident = f"CRIA-{prefix}-{date_str}-{i+1}"
        calf = Bovine(
            farm_id=farm_id,
            registered_by=user_id,
            identification_number=ident,
            sex=sex,
            birth_date=event.event_date,
            entry_type="nacimiento",
            entry_date=event.event_date,
            mother_id=event.bovine_id,
        )
        db.add(calf)
        db.flush()
        add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="bovine", entity_id=str(calf.id), details={"calf_from": "parto", "mother_id": str(event.bovine_id)})
        calves.append(calf)

    return calves


def list_events(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = None,
    event_type: str | None = None,
) -> Sequence[ReproductiveEvent]:
    stmt = select(ReproductiveEvent).where(ReproductiveEvent.farm_id == farm_id)
    if bovine_id:
        stmt = stmt.where(ReproductiveEvent.bovine_id == bovine_id)
    if event_type:
        stmt = stmt.where(ReproductiveEvent.event_type == event_type)
    stmt = stmt.order_by(ReproductiveEvent.event_date.desc())
    return db.execute(stmt).scalars().all()


def get_event(db: Session, farm_id: uuid.UUID, event_id: uuid.UUID) -> ReproductiveEvent:
    stmt = select(ReproductiveEvent).where(ReproductiveEvent.id == event_id, ReproductiveEvent.farm_id == farm_id)
    event = db.execute(stmt).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento reproductivo no encontrado")
    return event


def update_event(db: Session, farm_id: uuid.UUID, event_id: uuid.UUID, data: ReproductiveEventUpdate, user_id: uuid.UUID) -> ReproductiveEvent:
    event = get_event(db, farm_id, event_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    # ¿Qué? Recalcular la fecha probable de parto si pasó a "servicio".
    if event.event_type == "servicio" and event.due_date is None:
        event.due_date = event.event_date + timedelta(days=GESTATION_DAYS)

    # ¿Qué? Si se registra como parto y aún no hay cría, crear las crías.
    if event.event_type == "parto" and not event.calf_id:
        calves = _create_calves_from_birth(db, farm_id, event, user_id)
        if calves:
            event.calf_id = calves[0].id

    db.commit()
    db.refresh(event)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="update", entity="reproductive_event", entity_id=str(event.id), details={"type": event.event_type})
    db.commit()
    return event


def delete_event(db: Session, farm_id: uuid.UUID, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
    event = get_event(db, farm_id, event_id)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="delete", entity="reproductive_event", entity_id=str(event.id))
    db.delete(event)
    db.commit()
