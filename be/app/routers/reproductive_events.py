import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.reproductive_event import ReproductiveEventCreate, ReproductiveEventResponse, ReproductiveEventUpdate
from app.services import reproductive_event_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/reproductive-events", tags=["Eventos Reproductivos"])


@router.post("", response_model=ReproductiveEventResponse, status_code=status.HTTP_201_CREATED, summary="Registrar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: ReproductiveEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReproductiveEventResponse:
    event = reproductive_event_service.create_event(db, farm_id, data, current_user.id)
    return ReproductiveEventResponse.model_validate(event)


@router.get("", response_model=list[ReproductiveEventResponse], summary="Listar eventos reproductivos", dependencies=[Depends(require_permission("reproductivo", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    event_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReproductiveEventResponse]:
    _ = current_user
    events = reproductive_event_service.list_events(db, farm_id, bovine_id, event_type)
    return [ReproductiveEventResponse.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=ReproductiveEventResponse, summary="Obtener evento por ID", dependencies=[Depends(require_permission("reproductivo", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReproductiveEventResponse:
    _ = current_user
    event = reproductive_event_service.get_event(db, farm_id, event_id)
    return ReproductiveEventResponse.model_validate(event)


@router.put("/{event_id}", response_model=ReproductiveEventResponse, summary="Actualizar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_update"))])
def update(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    data: ReproductiveEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReproductiveEventResponse:
    event = reproductive_event_service.update_event(db, farm_id, event_id, data, current_user.id)
    return ReproductiveEventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar evento reproductivo", dependencies=[Depends(require_permission("reproductivo", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _ = current_user
    reproductive_event_service.delete_event(db, farm_id, event_id, current_user.id)
