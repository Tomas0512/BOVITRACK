"""
Módulo: routers/milk_production.py
¿Qué? Router de FastAPI para el CRUD de registros de producción lechera.
¿Para qué? Registrar los ordeños diarios, consultarlos y eliminar erróneos.
¿Impacto? Estos datos alimentan la vista v_milk_production_daily para
          reportes de producción por finca y por día.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.milk_production import MilkProductionCreate, MilkProductionResponse
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MilkProductionResponse]:
    """¿Qué? Lista los registros de ordeño con filtro opcional por bovino.
    ¿Para qué? Consultar historial de producción completo o de un animal.
    ¿Impacto? Ordenados por fecha descendente (más recientes primero).
    """
    _ = current_user
    records = milk_production_service.list_records(db, farm_id, bovine_id)
    return [MilkProductionResponse.model_validate(r) for r in records]


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
    milk_production_service.delete_record(db, farm_id, record_id)
