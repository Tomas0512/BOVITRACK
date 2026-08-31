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
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.farm import LandPlot
from app.models.milk_production import MilkProduction
from app.schemas.milk_production import MilkProductionCreate
from app.services.audit_service import add_audit_log


def create_record(db: Session, farm_id: uuid.UUID, data: MilkProductionCreate, user_id: uuid.UUID) -> MilkProduction:
    """¿Qué? Registra un nuevo ordeño en la base de datos.
    ¿Para qué? Capturar litros producidos, tipo de ordeño y bovino/potrero.
    ¿Impacto? registered_by permite saber quién registró el ordeño (auditoría).
    """
    # ¿Qué? Todo ordeño debe vincularse a un bovino o a un lote.
    if data.bovine_id is None and data.land_plot_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicar un bovino o un lote para el ordeño",
        )

    # ¿Qué? Validar que las referencias existan y pertenezcan a la finca.
    if data.bovine_id:
        bovine = db.execute(
            select(Bovine).where(Bovine.id == data.bovine_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not bovine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El bovino indicado no existe en esta finca",
            )
    if data.land_plot_id:
        land_plot = db.execute(
            select(LandPlot).where(LandPlot.id == data.land_plot_id, LandPlot.farm_id == farm_id)
        ).scalar_one_or_none()
        if not land_plot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote indicado no existe en esta finca",
            )

    # ¿Qué? Evitar registrar dos ordeños del mismo bovino/día/sesión.
    if data.bovine_id:
        duplicate = db.execute(
            select(MilkProduction.id).where(
                MilkProduction.bovine_id == data.bovine_id,
                MilkProduction.milking_date == data.milking_date,
                func.coalesce(MilkProduction.milking_session, "") == func.coalesce(data.milking_session, ""),
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un ordeño registrado para este bovino en esa fecha/sesión",
            )

    record = MilkProduction(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="milk_production", entity_id=str(record.id), details={"liters": str(record.quantity_liters)})
    db.commit()
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


def delete_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    """¿Qué? Elimina un registro de producción.
    ¿Para qué? Corregir registros erróneos de ordeño.
    ¿Impacto? La eliminación es permanente. Afecta los reportes de producción.
    """
    record = get_record(db, farm_id, record_id)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="delete", entity="milk_production", entity_id=str(record.id))
    db.delete(record)
    db.commit()
