"""
Módulo: modules/economics/router.py (frontera HTTP del módulo)
¿Qué? Endpoints de /api/v1/farms/{farm_id}/economics: CRUD de ingresos y
      egresos, más los indicadores económicos.
¿Para qué? Traducir HTTP <-> casos de uso de EconomicsService, exigiendo el
           permiso del módulo "economica".
¿Impacto? Sin reglas de negocio ni consultas. NotFoundError -> 404 lo traduce core.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.modules.economics.dependencies import get_current_user, get_economics_service, require_permission
from app.modules.economics.schemas import EconomicIndicators, EconomicRecordCreate, EconomicRecordResponse, EconomicRecordUpdate
from app.modules.economics.service import EconomicsService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/economics", tags=["Informacion Economica"])


@router.post("", response_model=EconomicRecordResponse, status_code=status.HTTP_201_CREATED, summary="Registrar movimiento economico", dependencies=[Depends(require_permission("economica", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: EconomicRecordCreate,
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EconomicRecordResponse:
    record = service.create_record(farm_id, data, current_user.id)
    return EconomicRecordResponse.model_validate(record)


@router.get("", response_model=list[EconomicRecordResponse], summary="Listar movimientos economicos", dependencies=[Depends(require_permission("economica", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    record_type: str | None = Query(None),
    category: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[EconomicRecordResponse]:
    _ = current_user
    records = service.list_records(farm_id, record_type, category, date_from, date_to)
    return [EconomicRecordResponse.model_validate(r) for r in records]


@router.get("/indicators", response_model=EconomicIndicators, summary="Indicadores economicos", dependencies=[Depends(require_permission("economica", "can_read"))])
def indicators(
    farm_id: uuid.UUID,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EconomicIndicators:
    _ = current_user
    return service.get_indicators(farm_id, date_from, date_to)


@router.get("/{record_id}", response_model=EconomicRecordResponse, summary="Obtener movimiento por ID", dependencies=[Depends(require_permission("economica", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EconomicRecordResponse:
    _ = current_user
    record = service.get_record(farm_id, record_id)
    return EconomicRecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=EconomicRecordResponse, summary="Actualizar movimiento economico", dependencies=[Depends(require_permission("economica", "can_update"))])
def update(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    data: EconomicRecordUpdate,
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> EconomicRecordResponse:
    record = service.update_record(farm_id, record_id, data, current_user.id)
    return EconomicRecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar movimiento economico", dependencies=[Depends(require_permission("economica", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    service: EconomicsService = Depends(get_economics_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    service.delete_record(farm_id, record_id, current_user.id)
