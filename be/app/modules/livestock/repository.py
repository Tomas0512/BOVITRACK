"""
Módulo: modules/livestock/repository.py
¿Qué? Acceso a datos del ganado: bovinos, pesajes y movimientos.
¿Para qué? Que los servicios pidan "los terneros de la finca nacidos después
           de tal fecha" o "el pesaje anterior a esta fecha" sin escribir
           consultas.
¿Impacto? Toda consulta por bovino, pesaje o movimiento filtra por farm_id.
"""

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.livestock.models import AnimalMovement, Bovine, Weight


class _UnitOfWork:
    """Operaciones de escritura comunes sobre la sesión."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, row: Bovine | Weight | AnimalMovement) -> None:
        self._db.add(row)

    def delete(self, row: Bovine | Weight | AnimalMovement) -> None:
        self._db.delete(row)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

    def refresh(self, row: Bovine | Weight | AnimalMovement) -> None:
        self._db.refresh(row)


class BovineRepository(_UnitOfWork):
    """Bovinos (incluye las consultas de terneros, que son bovinos jóvenes)."""

    def get_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine | None:
        """El bovino de la finca, activo o no."""
        stmt = select(Bovine).where(Bovine.id == bovine_id, Bovine.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_active_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine | None:
        """El bovino de la finca solo si está activo."""
        stmt = select(Bovine).where(Bovine.id == bovine_id, Bovine.farm_id == farm_id, Bovine.is_active.is_(True))
        return self._db.execute(stmt).scalar_one_or_none()

    def identification_taken(
        self, farm_id: uuid.UUID, identification_number: str, *, exclude_id: uuid.UUID | None = None
    ) -> bool:
        """¿Ya hay otro bovino de la finca con ese número de identificación?"""
        stmt = select(Bovine).where(Bovine.farm_id == farm_id, Bovine.identification_number == identification_number)
        if exclude_id is not None:
            stmt = stmt.where(Bovine.id != exclude_id)
        return self._db.execute(stmt).scalar_one_or_none() is not None

    def list_active(
        self,
        farm_id: uuid.UUID,
        *,
        sex: str | None = None,
        status: str | None = None,
        purpose: str | None = None,
    ) -> Sequence[Bovine]:
        """Bovinos activos de la finca, los registrados más recientemente primero."""
        stmt = select(Bovine).where(Bovine.farm_id == farm_id, Bovine.is_active.is_(True))
        if sex:
            stmt = stmt.where(Bovine.sex == sex)
        if status:
            stmt = stmt.where(Bovine.status == status)
        if purpose:
            stmt = stmt.where(Bovine.purpose == purpose)
        return self._db.execute(stmt.order_by(Bovine.created_at.desc())).scalars().all()

    def list_breeds(self, farm_id: uuid.UUID) -> list[str]:
        """Razas distintas (no vacías) ya registradas en la finca, en orden alfabético."""
        stmt = (
            select(Bovine.breed)
            .where(Bovine.farm_id == farm_id, Bovine.breed.isnot(None), Bovine.breed != "")
            .distinct()
            .order_by(Bovine.breed)
        )
        return list(self._db.execute(stmt).scalars().all())

    # ── Terneros ─────────────────────────────────────────────

    def list_active_born_between(
        self, farm_id: uuid.UUID, born_after: date, born_on_or_before: date, *, status: str | None = None
    ) -> Sequence[Bovine]:
        """Activos nacidos en (born_after, born_on_or_before], los más jóvenes primero."""
        stmt = select(Bovine).where(
            Bovine.farm_id == farm_id,
            Bovine.is_active.is_(True),
            Bovine.birth_date > born_after,
            Bovine.birth_date <= born_on_or_before,
        )
        if status:
            stmt = stmt.where(Bovine.status == status)
        return self._db.execute(stmt.order_by(Bovine.birth_date.desc())).scalars().all()

    def count_active_born(self, farm_id: uuid.UUID, born_after: date, born_on_or_before: date | None = None) -> int:
        stmt = select(func.count(Bovine.id)).where(
            Bovine.farm_id == farm_id, Bovine.is_active.is_(True), Bovine.birth_date > born_after
        )
        if born_on_or_before is not None:
            stmt = stmt.where(Bovine.birth_date <= born_on_or_before)
        return self._db.execute(stmt).scalar() or 0

    def avg_current_weight_born_after(self, farm_id: uuid.UUID, born_after: date) -> object:
        stmt = select(func.avg(Bovine.current_weight)).where(
            Bovine.farm_id == farm_id, Bovine.is_active.is_(True), Bovine.birth_date > born_after
        )
        return self._db.execute(stmt).scalar()


class WeightRepository(_UnitOfWork):
    """Pesajes."""

    def get_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, weight_id: uuid.UUID) -> Weight | None:
        stmt = select(Weight).where(Weight.id == weight_id, Weight.farm_id == farm_id, Weight.bovine_id == bovine_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def previous_before(self, bovine_id: uuid.UUID, measured_at: date) -> Weight | None:
        """El pesaje más reciente ANTERIOR a la fecha dada."""
        stmt = (
            select(Weight)
            .where(Weight.bovine_id == bovine_id, Weight.measured_at < measured_at)
            .order_by(Weight.measured_at.desc())
            .limit(1)
        )
        return self._db.execute(stmt).scalars().first()

    def latest(self, bovine_id: uuid.UUID) -> Weight | None:
        """El pesaje más reciente del bovino."""
        stmt = select(Weight).where(Weight.bovine_id == bovine_id).order_by(Weight.measured_at.desc()).limit(1)
        return self._db.execute(stmt).scalars().first()

    def latest_measured_at(self, bovine_id: uuid.UUID) -> date | None:
        """Fecha del pesaje más reciente del bovino (lo ya guardado o enviado a la BD)."""
        return self._db.execute(select(func.max(Weight.measured_at)).where(Weight.bovine_id == bovine_id)).scalar()

    def exists_on_date(self, bovine_id: uuid.UUID, measured_at: date) -> bool:
        stmt = select(Weight.id).where(Weight.bovine_id == bovine_id, Weight.measured_at == measured_at)
        return self._db.execute(stmt.limit(1)).scalars().first() is not None

    def list_for_bovine(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, *, since: date | None = None) -> Sequence[Weight]:
        """Pesajes del bovino en orden cronológico (del más antiguo al más reciente)."""
        stmt = select(Weight).where(Weight.farm_id == farm_id, Weight.bovine_id == bovine_id)
        if since is not None:
            stmt = stmt.where(Weight.measured_at >= since)
        return self._db.execute(stmt.order_by(Weight.measured_at.asc())).scalars().all()

    def avg_daily_gain_of_calves(self, farm_id: uuid.UUID, born_after: date, measured_since: date) -> object:
        """Ganancia diaria promedio de los terneros activos en los pesajes recientes."""
        stmt = (
            select(func.avg(Weight.daily_gain))
            .join(Bovine, Weight.bovine_id == Bovine.id)
            .where(
                Weight.farm_id == farm_id,
                Bovine.farm_id == farm_id,
                Bovine.is_active.is_(True),
                Bovine.birth_date > born_after,
                Weight.measured_at >= measured_since,
            )
        )
        return self._db.execute(stmt).scalar()


class MovementRepository(_UnitOfWork):
    """Movimientos de entrada y salida."""

    def get_in_farm(self, farm_id: uuid.UUID, movement_id: uuid.UUID) -> AnimalMovement | None:
        stmt = select(AnimalMovement).where(AnimalMovement.id == movement_id, AnimalMovement.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_farm(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        movement_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Sequence[AnimalMovement]:
        stmt = select(AnimalMovement).where(AnimalMovement.farm_id == farm_id)
        if bovine_id:
            stmt = stmt.where(AnimalMovement.bovine_id == bovine_id)
        if movement_type:
            stmt = stmt.where(AnimalMovement.movement_type == movement_type)
        if date_from:
            stmt = stmt.where(AnimalMovement.movement_date >= date_from)
        if date_to:
            stmt = stmt.where(AnimalMovement.movement_date <= date_to)
        stmt = stmt.order_by(AnimalMovement.movement_date.desc(), AnimalMovement.created_at.desc())
        return self._db.execute(stmt).scalars().all()

    def duplicate_exists(self, bovine_id: uuid.UUID, movement_type: str, movement_date: date) -> bool:
        stmt = select(AnimalMovement.id).where(
            AnimalMovement.bovine_id == bovine_id,
            AnimalMovement.movement_type == movement_type,
            AnimalMovement.movement_date == movement_date,
        )
        return self._db.execute(stmt).scalar_one_or_none() is not None
