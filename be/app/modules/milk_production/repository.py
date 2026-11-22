"""
Módulo: modules/milk_production/repository.py
¿Qué? Acceso a datos de la tabla `milk_production`.
¿Para qué? Que el servicio pida "los ordeños de la finca", "¿ya hay un ordeño
           de este bovino en esa fecha y sesión?" sin escribir consultas.
¿Impacto? Toda consulta por registro o listado filtra por farm_id.
"""

import uuid
from collections.abc import Sequence
from datetime import date, datetime

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.modules.milk_production.models import MilkProduction


class MilkProductionRepository:
    """Repositorio de ordeños sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, record_id: uuid.UUID) -> MilkProduction | None:
        """El ordeño si existe y pertenece a la finca; si no, None."""
        stmt = select(MilkProduction).where(MilkProduction.id == record_id, MilkProduction.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        milking_session: str | None = None,
        milking_type: str | None = None,
        newest_first: bool = True,
    ) -> Sequence[MilkProduction]:
        """Ordeños de la finca con filtros. Las fechas se comparan por día (inclusivas)."""
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
        if newest_first:
            stmt = stmt.order_by(MilkProduction.milking_date.desc())
        return self._db.execute(stmt).scalars().all()

    def exists_for_bovine_session(
        self,
        bovine_id: uuid.UUID,
        milking_date: datetime,
        milking_session: str | None,
        *,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        """¿Ya hay un ordeño del bovino en esa fecha y sesión? (sesión vacía = sin sesión)."""
        stmt = select(MilkProduction.id).where(
            MilkProduction.bovine_id == bovine_id,
            MilkProduction.milking_date == milking_date,
            func.coalesce(MilkProduction.milking_session, "") == func.coalesce(milking_session, ""),
        )
        if exclude_id is not None:
            stmt = stmt.where(MilkProduction.id != exclude_id)
        # .first() y no scalar_one_or_none(): si la BD ya tuviera dos duplicados
        # (datos viejos), la respuesta debe ser "sí hay duplicado" (400), no un 500.
        return self._db.execute(stmt.limit(1)).scalars().first() is not None

    def add(self, record: MilkProduction) -> None:
        self._db.add(record)

    def delete(self, record: MilkProduction) -> None:
        self._db.delete(record)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, record: MilkProduction) -> None:
        self._db.refresh(record)
