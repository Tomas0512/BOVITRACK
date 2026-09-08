"""
Módulo: services/milk_production_service.py
¿Qué? Capa de servicio para el módulo de producción lechera.
¿Para qué? Registrar y consultar los ordeños diarios de cada bovino/potrero.
¿Impacto? Los reportes de producción diaria (vista v_milk_production_daily)
          dependen directamente de estos registros.
"""

import uuid
from datetime import date
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.farm import LandPlot
from app.models.milk_production import MilkProduction
from app.schemas.milk_production import MilkProductionCreate, MilkProductionUpdate
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


def list_records(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    milking_session: str | None = None,
    milking_type: str | None = None,
) -> Sequence[MilkProduction]:
    """¿Qué? Lista los registros de producción de una finca.
    ¿Para qué? Consultar el historial de ordeños, filtrable por bovino,
               rango de fechas, sesión y tipo de ordeño.
    ¿Impacto? Filtros de rango (date_from/date_to) son inclusivos sobre la fecha
              local del ordeño; ordenados por fecha descendente.
    """
    stmt = select(MilkProduction).where(MilkProduction.farm_id == farm_id)
    if bovine_id:
        stmt = stmt.where(MilkProduction.bovine_id == bovine_id)
    if date_from:
        stmt = stmt.where(cast(MilkProduction.milking_date, Date) >= date_from)
    if date_to:
        stmt = stmt.where(cast(MilkProduction.milking_date, Date) <= date_to)
    if milking_session:
        stmt = stmt.where(MilkProduction.milking_session == milking_session)
    if milking_type:
        stmt = stmt.where(MilkProduction.milking_type == milking_type)
    stmt = stmt.order_by(MilkProduction.milking_date.desc())
    return db.execute(stmt).scalars().all()


def update_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID, data: MilkProductionUpdate, user_id: uuid.UUID) -> MilkProduction:
    """¿Qué? Actualiza un ordeño existente en la base de datos.
    ¿Para qué? Corregir litros, fecha, tipo, sesión u observaciones.
    ¿Impacto? Revalida referencias y duplicados del mismo bovino/fecha/sesión.
    """
    record = get_record(db, farm_id, record_id)

    payload = data.model_dump(exclude_unset=True)

    if "bovine_id" in payload:
        if payload.get("bovine_id") is None and payload.get("land_plot_id") is None and record.land_plot_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe indicar un bovino o un lote para el ordeño",
            )
        if payload.get("bovine_id"):
            bovine = db.execute(
                select(Bovine).where(Bovine.id == payload["bovine_id"], Bovine.farm_id == farm_id)
            ).scalar_one_or_none()
            if not bovine:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El bovino indicado no existe en esta finca",
                )

    if "land_plot_id" in payload and payload.get("land_plot_id"):
        land_plot = db.execute(
            select(LandPlot).where(LandPlot.id == payload["land_plot_id"], LandPlot.farm_id == farm_id)
        ).scalar_one_or_none()
        if not land_plot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote indicado no existe en esta finca",
            )

    new_bovine = payload.get("bovine_id", record.bovine_id)
    new_date = payload.get("milking_date", record.milking_date)
    new_session = payload.get("milking_session", record.milking_session)

    if new_bovine:
        duplicate = db.execute(
            select(MilkProduction.id).where(
                MilkProduction.bovine_id == new_bovine,
                MilkProduction.milking_date == new_date,
                func.coalesce(MilkProduction.milking_session, "") == func.coalesce(new_session, ""),
                MilkProduction.id != record_id,
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un ordeño registrado para este bovino en esa fecha/sesión",
            )

    for key, value in payload.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="update", entity="milk_production", entity_id=str(record.id), details={"liters": str(record.quantity_liters)})
    db.commit()
    return record


def get_milk_summary(db: Session, farm_id: uuid.UUID, date_from: date | None = None, date_to: date | None = None) -> dict:
    """¿Qué? Resumen agregado de la producción en un periodo.
    ¿Para qué? Alimentar KPIs y gráficas del dashboard de producción lechera:
               total litros, promedio diario, registros y producción por sesión.
    ¿Impacto? Filtrable por rango de fechas; todo a nivel finca.
    """
    base = select(MilkProduction).where(MilkProduction.farm_id == farm_id)
    if date_from:
        base = base.where(cast(MilkProduction.milking_date, Date) >= date_from)
    if date_to:
        base = base.where(cast(MilkProduction.milking_date, Date) <= date_to)

    rows = db.execute(base).scalars().all()
    if not rows:
        return {
            "total_liters": "0",
            "avg_daily_liters": "0",
            "total_records": 0,
            "milking_days": 0,
            "by_session": {},
            "by_type": {},
            "top_bovines": [],
        }

    total = sum(r.quantity_liters for r in rows)
    days = {r.milking_date.date() for r in rows}
    by_session: dict[str, Decimal] = {}
    by_type: dict[str, Decimal] = {}
    per_bovine: dict[uuid.UUID, Decimal] = {}

    for r in rows:
        session = r.milking_session or "sin_sesión"
        by_session[session] = by_session.get(session, 0) + r.quantity_liters
        by_type[r.milking_type] = by_type.get(r.milking_type, 0) + r.quantity_liters
        if r.bovine_id:
            per_bovine[r.bovine_id] = per_bovine.get(r.bovine_id, 0) + r.quantity_liters

    top = sorted(per_bovine.items(), key=lambda kv: kv[1], reverse=True)[:10]
    top_list = [
        {"bovine_id": str(bid), "total_liters": str(amount)}
        for bid, amount in top
    ]

    return {
        "total_liters": str(total),
        "avg_daily_liters": str((total / len(days)).quantize(Decimal("0.01"))) if days else "0",
        "total_records": len(rows),
        "milking_days": len(days),
        "by_session": {k: str(v) for k, v in by_session.items()},
        "by_type": {k: str(v) for k, v in by_type.items()},
        "top_bovines": top_list,
    }


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
