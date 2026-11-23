"""
Módulo: modules/reproduction/repository.py
¿Qué? Acceso a datos de la tabla `reproductive_event`.
¿Para qué? Que el servicio pida "los eventos de la finca" o "el evento X" sin
           escribir consultas.
¿Impacto? Toda consulta filtra por farm_id.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.reproduction.models import ReproductiveEvent


class ReproductiveEventRepository:
    """Repositorio de eventos reproductivos sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, event_id: uuid.UUID) -> ReproductiveEvent | None:
        stmt = select(ReproductiveEvent).where(ReproductiveEvent.id == event_id, ReproductiveEvent.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        event_type: str | None = None,
    ) -> Sequence[ReproductiveEvent]:
        """Eventos de la finca, los más recientes primero."""
        stmt = select(ReproductiveEvent).where(ReproductiveEvent.farm_id == farm_id)
        if bovine_id:
            stmt = stmt.where(ReproductiveEvent.bovine_id == bovine_id)
        if event_type:
            stmt = stmt.where(ReproductiveEvent.event_type == event_type)
        stmt = stmt.order_by(ReproductiveEvent.event_date.desc())
        return self._db.execute(stmt).scalars().all()

    def add(self, event: ReproductiveEvent) -> None:
        self._db.add(event)

    def delete(self, event: ReproductiveEvent) -> None:
        self._db.delete(event)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, event: ReproductiveEvent) -> None:
        self._db.refresh(event)
