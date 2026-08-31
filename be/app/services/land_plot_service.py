"""
Módulo: services/land_plot_service.py
¿Qué? Capa de servicio para lotes de una finca.
¿Para qué? Gestionar el CRUD de lotes, validando nombres únicos por finca.
¿Impacto? Los bovinos referencian land_plot_id; sin lotes no se puede
          organizar el hato por área.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import LandPlot
from app.models.paddock import Paddock
from app.schemas.land_plot import LandPlotCreate, LandPlotUpdate
from app.services.audit_service import add_audit_log


def create_land_plot(db: Session, farm_id: uuid.UUID, data: LandPlotCreate, user_id: uuid.UUID | None = None) -> LandPlot:
    existing = db.execute(
        select(LandPlot).where(LandPlot.farm_id == farm_id, LandPlot.name == data.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un lote con ese nombre en esta finca")

    payload = data.model_dump()
    potreros = payload.pop("paddocks", [])

    # Los nombres de potrero son únicos por finca: se valida antes de escribir
    # nada, para no dejar el lote a medias.
    nombres = [p["name"] for p in potreros]
    choque = db.execute(
        select(Paddock.name).where(Paddock.farm_id == farm_id, Paddock.name.in_(nombres))
    ).scalars().first()
    if choque:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un potrero llamado '{choque}' en esta finca",
        )

    # Lote y potreros entran en la MISMA transacción: si algo falla, no queda
    # un lote huérfano sin potreros.
    lp = LandPlot(farm_id=farm_id, **payload)
    db.add(lp)
    db.flush()  # asigna lp.id sin confirmar todavía

    for p in potreros:
        db.add(Paddock(farm_id=farm_id, land_plot_id=lp.id, **p))

    add_audit_log(
        db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id),
        action="create", entity="land_plot", entity_id=str(lp.id),
        details={"name": lp.name, "paddocks": nombres},
    )
    db.commit()
    db.refresh(lp)
    return lp


def list_land_plots(db: Session, farm_id: uuid.UUID, *, is_active: bool | None = None) -> Sequence[LandPlot]:
    stmt = select(LandPlot).where(LandPlot.farm_id == farm_id)
    if is_active is not None:
        stmt = stmt.where(LandPlot.is_active.is_(is_active))
    stmt = stmt.order_by(LandPlot.name.asc())
    return db.execute(stmt).scalars().all()


def get_land_plot(db: Session, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> LandPlot:
    lp = db.execute(
        select(LandPlot).where(LandPlot.id == land_plot_id, LandPlot.farm_id == farm_id)
    ).scalar_one_or_none()
    if not lp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado")
    return lp


def update_land_plot(db: Session, farm_id: uuid.UUID, land_plot_id: uuid.UUID, data: LandPlotUpdate, user_id: uuid.UUID | None = None) -> LandPlot:
    lp = get_land_plot(db, farm_id, land_plot_id)
    if data.name is not None and data.name != lp.name:
        conflict = db.execute(
            select(LandPlot).where(LandPlot.farm_id == farm_id, LandPlot.name == data.name, LandPlot.id != land_plot_id)
        ).scalar_one_or_none()
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un lote con ese nombre en esta finca")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lp, field, value)
    db.commit()
    db.refresh(lp)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="update", entity="land_plot", entity_id=str(lp.id), details={"name": lp.name})
    db.commit()
    return lp


def delete_land_plot(db: Session, farm_id: uuid.UUID, land_plot_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    lp = get_land_plot(db, farm_id, land_plot_id)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="delete", entity="land_plot", entity_id=str(lp.id), details={"name": lp.name})
    db.delete(lp)
    db.commit()
