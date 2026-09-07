"""
Módulo: routers/milk_production.py
¿Qué? Router de FastAPI para el CRUD de registros de producción lechera.
¿Para qué? Registrar los ordeños diarios, consultarlos y eliminar erróneos.
¿Impacto? Estos datos alimentan la vista v_milk_production_daily para
          reportes de producción por finca y por día.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.milk_production import MilkProductionCreate, MilkProductionResponse, MilkProductionUpdate
from app.services import milk_production_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/milk-production", tags=["Producción Lechera"])


@router.post("", response_model=MilkProductionResponse, status_code=status.HTTP_201_CREATED, summary="Registrar ordeño", dependencies=[Depends(require_permission("produccion_leche", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: MilkProductionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MilkProductionResponse:
    """¿Qué? Registra un nuevo ordeño asociado a un bovino y/o potrero.
    ¿Para qué? Capturar litros producidos, tipo (manual/mecánico) y quién registró.
    ¿Impacto? Retorna 201 Created. Los litros se validan > 0 en el schema.
    """
    record = milk_production_service.create_record(db, farm_id, data, current_user.id)
    return MilkProductionResponse.model_validate(record)


@router.get("", response_model=list[MilkProductionResponse], summary="Listar registros de producción", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None, description="Filtro desde (YYYY-MM-DD, inclusivo)"),
    date_to: date | None = Query(None, description="Filtro hasta (YYYY-MM-DD, inclusivo)"),
    milking_session: str | None = Query(None, description="Sesión: mañana, tarde o noche"),
    milking_type: str | None = Query(None, description="Tipo: manual o mecanico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MilkProductionResponse]:
    """¿Qué? Lista los registros de ordeño con filtro opcional por bovino,
    rango de fechas, sesión y tipo de ordeño.
    ¿Para qué? Consultar historial de producción completo o acotado.
    ¿Impacto? Ordenados por fecha descendente (más recientes primero).
    """
    _ = current_user
    records = milk_production_service.list_records(
        db,
        farm_id,
        bovine_id=bovine_id,
        date_from=date_from,
        date_to=date_to,
        milking_session=milking_session,
        milking_type=milking_type,
    )
    return [MilkProductionResponse.model_validate(r) for r in records]


@router.get("/summary", summary="Resumen de producción en periodo", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def summary(
    farm_id: uuid.UUID,
    date_from: date | None = Query(None, description="Filtro desde (YYYY-MM-DD, inclusivo)"),
    date_to: date | None = Query(None, description="Filtro hasta (YYYY-MM-DD, inclusivo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """¿Qué? Retorna KPIs agregados de producción lechera del periodo.
    ¿Para qué? Alimentar el dashboard de producción (totales, promedios, sesión).
    ¿Impacto? Debe declararse antes de /{record_id} para no chocar con la ruta UUID.
    """
    _ = current_user
    return milk_production_service.get_milk_summary(db, farm_id, date_from=date_from, date_to=date_to)


@router.get("/{record_id}", response_model=MilkProductionResponse, summary="Obtener registro por ID", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MilkProductionResponse:
    """¿Qué? Retorna el detalle de un registro de producción.
    ¿Para qué? Ver detalles del ordeño (litros, tipo, sesión).
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    record = milk_production_service.get_record(db, farm_id, record_id)
    return MilkProductionResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar registro de producción", dependencies=[Depends(require_permission("produccion_leche", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina un registro de ordeño registrado por error.
    ¿Para qué? Corrección de datos. Eliminación permanente.
    ¿Impacto? Afecta los totales en reportes de producción diaria.
    """
    _ = current_user
    milk_production_service.delete_record(db, farm_id, record_id, current_user.id)


@router.put("/{record_id}", response_model=MilkProductionResponse, summary="Actualizar registro de producción", dependencies=[Depends(require_permission("produccion_leche", "can_update"))])
def update(
    farm_id: uuid.UUID,
    record_id: uuid.UUID,
    data: MilkProductionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MilkProductionResponse:
    """¿Qué? Actualiza un ordeño existente (litros, fecha, sesión, tipo...).
    ¿Para qué? Corregir datos operativos de la producción lechera.
    ¿Impacto? Patch parcial (exclude_unset); valida referencias y duplicados.
    """
    record = milk_production_service.update_record(db, farm_id, record_id, data, current_user.id)
    return MilkProductionResponse.model_validate(record)
