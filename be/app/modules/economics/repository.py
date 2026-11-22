"""
Módulo: modules/economics/repository.py
¿Qué? Acceso a datos de la tabla `economic_record`.
¿Para qué? Que el servicio pida "los movimientos de la finca en este rango"
           sin escribir consultas. Es la única capa del módulo que conoce la sesión.
¿Impacto? Toda consulta filtra por farm_id.
"""

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.economics.models import EconomicRecord


class EconomicRecordRepository:
    """Repositorio de movimientos económicos sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, record_id: uuid.UUID) -> EconomicRecord | None:
        """Devuelve el movimiento si existe y pertenece a la finca; si no, None."""
        stmt = select(EconomicRecord).where(EconomicRecord.id == record_id, EconomicRecord.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        record_type: str | None = None,
        category: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        newest_first: bool = True,
    ) -> Sequence[EconomicRecord]:
        """Lista los movimientos de la finca con filtros opcionales."""
        stmt = select(EconomicRecord).where(EconomicRecord.farm_id == farm_id)
        if record_type:
            stmt = stmt.where(EconomicRecord.record_type == record_type)
        if category:
            stmt = stmt.where(EconomicRecord.category == category)
        if date_from:
            stmt = stmt.where(EconomicRecord.record_date >= date_from)
        if date_to:
            stmt = stmt.where(EconomicRecord.record_date <= date_to)
        if newest_first:
            stmt = stmt.order_by(EconomicRecord.record_date.desc())
        return self._db.execute(stmt).scalars().all()

    def add(self, record: EconomicRecord) -> None:
        self._db.add(record)

    def delete(self, record: EconomicRecord) -> None:
        self._db.delete(record)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, record: EconomicRecord) -> None:
        self._db.refresh(record)
