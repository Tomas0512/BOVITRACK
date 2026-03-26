"""
Módulo: services/milk_production_service.py
¿Qué? Capa de servicio para el módulo de producción lechera.
¿Para qué? Registrar y consultar los ordeños diarios de cada bovino/potrero.
¿Impacto? Los reportes de producción diaria (vista v_milk_production_daily)
          dependen directamente de estos registros.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.milk_production import MilkProduction
from app.schemas.milk_production import MilkProductionCreate


def create_record(db: Session, farm_id: uuid.UUID, data: MilkProductionCreate, user_id: uuid.UUID) -> MilkProduction:
    """¿Qué? Registra un nuevo ordeño en la base de datos.
    ¿Para qué? Capturar litros producidos, tipo de ordeño y bovino/potrero.
    ¿Impacto? registered_by permite saber quién registró el ordeño (auditoría).
    """
    record = MilkProduction(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID | None = None) -> Sequence[MilkProduction]:
    """¿Qué? Lista los registros de producción de una finca.
    ¿Para qué? Consultar el historial de ordeños, filtrable por bovino.
    ¿Impacto? Ordenados por fecha descendente para ver los más recientes primero.
    """
    stmt = select(MilkProduction).where(MilkProduction.farm_id == farm_id)
    if bovine_id:
        stmt = stmt.where(MilkProduction.bovine_id == bovine_id)
    stmt = stmt.order_by(MilkProduction.milking_date.desc())
    return db.execute(stmt).scalars().all()


def get_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID) -> MilkProduction:
    """¿Qué? Obtiene un registro de producción por ID.
    ¿Para qué? Consultar detalle o validar existencia antes de eliminar.
    ¿Impacto? Filtra por farm_id para seguridad entre fincas.
    """
    stmt = select(MilkProduction).where(MilkProduction.id == record_id, MilkProduction.farm_id == farm_id)
    record = db.execute(stmt).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de producción no encontrado")
    return record


def delete_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID) -> None:
    """¿Qué? Elimina un registro de producción.
    ¿Para qué? Corregir registros erróneos de ordeño.
    ¿Impacto? La eliminación es permanente. Afecta los reportes de producción.
    """
    record = get_record(db, farm_id, record_id)
    db.delete(record)
    db.commit()
