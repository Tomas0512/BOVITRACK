import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.economics import EconomicRecordCreate, EconomicRecordResponse, EconomicRecordUpdate, EconomicIndicators
from app.services import economics_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/economics", tags=["Informacion Economica"])


@router.post("", response_model=EconomicRecordResponse, status_code=status.HTTP_201_CREATED, summary="Registrar movimiento economico", dependencies=[Depends(require_permission("economica", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: EconomicRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EconomicRecordResponse:
    record = economics_service.create_record(db, farm_id, data, current_user.id)
    return EconomicRecordResponse.model_validate(record)


@router.get("", response_model=list[EconomicRecordResponse], summary="Listar movimientos economicos", dependencies=[Depends(require_permission("economica", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    record_type: str | None = Query(None),
    category: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EconomicRecordResponse]:
    _ = current_user
    records = economics_service.list_records(db, farm_id, record_type, category, date_from, date_to)
    return [EconomicRecordResponse.model_validate(r) for r in records]


@router.get("/indicators", response_model=EconomicIndicators, summary="Indicadores economicos", dependencies=[Depends(require_permission("economica", "can_read"))])
def indicators(
    farm_id: uuid.UUID,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EconomicIndicators:
    _ = current_user
    return economics_service.get_indicators(db, farm_id, date_from, date_to)


@router.get("/{record_id}", response_model=EconomicRecordResponse, summary="Obtener movimiento por ID", dependencies=[Depends(require_permission("economica", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EconomicRecordResponse:
    _ = current_user
    record = economics_service.get_record(db, farm_id, record_id)
    return EconomicRecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=EconomicRecordResponse, summary="Actualizar movimiento economico", dependencies=[Depends(require_permission("economica", "can_update"))])
def update(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    data: EconomicRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EconomicRecordResponse:
    record = economics_service.update_record(db, farm_id, record_id, data, current_user.id)
    return EconomicRecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar movimiento economico", dependencies=[Depends(require_permission("economica", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    economics_service.delete_record(db, farm_id, record_id, current_user.id)
