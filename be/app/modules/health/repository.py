"""
Módulo: modules/health/repository.py
¿Qué? Acceso a datos de los dos agregados de salud: tratamientos aplicados
      (`treatment`) y planes sanitarios programados (`sanitary_plan`).
¿Para qué? Que los servicios pidan "el plan X de la finca" o "los planes
           vencidos" sin escribir consultas.
¿Impacto? Toda consulta filtra por farm_id.
"""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.health.models import SanitaryPlan, Treatment


class _UnitOfWork:
    """Operaciones comunes de escritura sobre la sesión."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, row: Treatment | SanitaryPlan) -> None:
        self._db.add(row)

    def delete(self, row: Treatment | SanitaryPlan) -> None:
        self._db.delete(row)

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, row: Treatment | SanitaryPlan) -> None:
        self._db.refresh(row)


class TreatmentRepository(_UnitOfWork):
    """Tratamientos aplicados."""

    def get_in_farm(self, farm_id: uuid.UUID, treatment_id: uuid.UUID) -> Treatment | None:
        stmt = select(Treatment).where(Treatment.id == treatment_id, Treatment.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(self, farm_id: uuid.UUID, *, bovine_id: uuid.UUID | None = None) -> Sequence[Treatment]:
        """Tratamientos de la finca, los más recientes primero."""
        stmt = select(Treatment).where(Treatment.farm_id == farm_id)
        if bovine_id:
            stmt = stmt.where(Treatment.bovine_id == bovine_id)
        return self._db.execute(stmt.order_by(Treatment.application_date.desc())).scalars().all()


class SanitaryPlanRepository(_UnitOfWork):
    """Planes sanitarios programados."""

    def get_in_farm(self, farm_id: uuid.UUID, plan_id: uuid.UUID) -> SanitaryPlan | None:
        stmt = select(SanitaryPlan).where(SanitaryPlan.id == plan_id, SanitaryPlan.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        land_plot_id: uuid.UUID | None = None,
        include_inactive: bool = False,
    ) -> Sequence[SanitaryPlan]:
        """Planes de la finca, del más próximo a aplicar al más lejano."""
        stmt = select(SanitaryPlan).where(SanitaryPlan.farm_id == farm_id)
        if not include_inactive:
            stmt = stmt.where(SanitaryPlan.is_active.is_(True))
        if bovine_id:
            stmt = stmt.where(SanitaryPlan.bovine_id == bovine_id)
        if land_plot_id:
            stmt = stmt.where(SanitaryPlan.land_plot_id == land_plot_id)
        return self._db.execute(stmt.order_by(SanitaryPlan.next_scheduled_date.asc())).scalars().all()

    def overdue(self, farm_id: uuid.UUID, now: datetime) -> Sequence[SanitaryPlan]:
        """Planes activos cuya próxima aplicación ya pasó."""
        stmt = select(SanitaryPlan).where(
            SanitaryPlan.farm_id == farm_id,
            SanitaryPlan.is_active.is_(True),
            SanitaryPlan.next_scheduled_date < now,
        )
        return self._db.execute(stmt).scalars().all()

    def upcoming(self, farm_id: uuid.UUID, now: datetime, until: datetime) -> Sequence[SanitaryPlan]:
        """Planes activos con aplicación entre ahora y `until`."""
        stmt = select(SanitaryPlan).where(
            SanitaryPlan.farm_id == farm_id,
            SanitaryPlan.is_active.is_(True),
            SanitaryPlan.next_scheduled_date >= now,
            SanitaryPlan.next_scheduled_date <= until,
        )
        return self._db.execute(stmt).scalars().all()
