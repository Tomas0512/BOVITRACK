"""
Módulo: modules/farms/repository.py (acceso a datos de farms)
¿Qué? Consultas de fincas, catálogos, lotes y potreros, y las que responden los
      puertos que farms ofrece a otros módulos (¿este lote es de la finca?...).
¿Para qué? Que los servicios no escriban SQL.
¿Impacto? Los animales de cada potrero se leen de la tabla `bovine` por el
          esquema (Base.metadata), sin importar el módulo livestock: farms está
          por DEBAJO de livestock y no puede depender de él. Es un modelo de
          lectura, igual que hacen reports y audit.
"""

from __future__ import annotations  # permite métodos llamados list sin tapar el tipo list

import uuid
from collections.abc import Sequence

from sqlalchemy import Table, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import Base
from app.modules.farms.models import City, Department, Farm, LandPlot, Paddock, Purpose


class FarmRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active(self, farm_id: uuid.UUID) -> Farm | None:
        stmt = select(Farm).where(Farm.id == farm_id, Farm.is_active.is_(True))
        return self._db.execute(stmt).scalar_one_or_none()

    def by_identifier(self, identifier: str, *, exclude_id: uuid.UUID | None = None) -> Farm | None:
        stmt = select(Farm).where(Farm.farm_identifier == identifier)
        if exclude_id is not None:
            stmt = stmt.where(Farm.id != exclude_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def by_location(
        self, name: str, department_id: uuid.UUID, city: str, *, exclude_id: uuid.UUID | None = None
    ) -> Farm | None:
        """La finca con ese nombre en ese departamento y municipio (restricción uq_farm_name_location)."""
        stmt = select(Farm).where(
            Farm.name == name, Farm.department_id == department_id, Farm.city_municipality == city
        )
        if exclude_id is not None:
            stmt = stmt.where(Farm.id != exclude_id)
        return self._db.execute(stmt).scalars().first()

    def list_visible(self, user_id: uuid.UUID, member_farm_ids: Sequence[uuid.UUID]) -> list[Farm]:
        """Fincas activas donde el usuario es dueño o miembro activo, las más nuevas primero."""
        stmt = (
            select(Farm)
            .where(Farm.is_active.is_(True), (Farm.owner_id == user_id) | Farm.id.in_(list(member_farm_ids)))
            .order_by(Farm.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def name_of(self, farm_id: uuid.UUID) -> str | None:
        return self._db.execute(select(Farm.name).where(Farm.id == farm_id)).scalar_one_or_none()

    def owner_id(self, farm_id: uuid.UUID) -> uuid.UUID | None:
        return self._db.execute(select(Farm.owner_id).where(Farm.id == farm_id)).scalar_one_or_none()

    def active_ids(self) -> list[uuid.UUID]:
        """IDs de todas las fincas activas (los recorre la tarea programada de alertas)."""
        return list(self._db.execute(select(Farm.id).where(Farm.is_active.is_(True))).scalars().all())

    def add(self, farm: Farm) -> None:
        self._db.add(farm)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

    def refresh(self, farm: Farm) -> None:
        self._db.refresh(farm)


class CatalogRepository:
    """Catálogos de solo lectura para los formularios."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def departments(self) -> list[Department]:
        return list(self._db.execute(select(Department).order_by(Department.name.asc())).scalars().all())

    def cities(self, department_id: uuid.UUID) -> list[City]:
        stmt = select(City).where(City.department_id == department_id).order_by(City.name.asc())
        return list(self._db.execute(stmt).scalars().all())

    def purposes(self) -> list[Purpose]:
        return list(self._db.execute(select(Purpose).order_by(Purpose.name.asc())).scalars().all())


class LandPlotRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID, *, only_active: bool = False) -> LandPlot | None:
        stmt = select(LandPlot).where(LandPlot.id == land_plot_id, LandPlot.farm_id == farm_id)
        if only_active:
            stmt = stmt.where(LandPlot.is_active.is_(True))
        return self._db.execute(stmt).scalar_one_or_none()

    def by_name(self, farm_id: uuid.UUID, name: str, *, exclude_id: uuid.UUID | None = None) -> LandPlot | None:
        stmt = select(LandPlot).where(LandPlot.farm_id == farm_id, LandPlot.name == name)
        if exclude_id is not None:
            stmt = stmt.where(LandPlot.id != exclude_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[LandPlot]:
        stmt = select(LandPlot).where(LandPlot.farm_id == farm_id)
        if is_active is not None:
            stmt = stmt.where(LandPlot.is_active.is_(is_active))
        return list(self._db.execute(stmt.order_by(LandPlot.name.asc())).scalars().all())

    # ── Puertos
    def exists_in_farm(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> bool:
        """LandPlotLookup: True si el lote existe y es de la finca."""
        return self.get_in_farm(farm_id, land_plot_id) is not None

    def id_by_name(self, farm_id: uuid.UUID, name: str) -> uuid.UUID | None:
        """Id del lote de la finca con ese nombre (sin distinguir mayúsculas), o None."""
        stmt = select(LandPlot.id).where(LandPlot.farm_id == farm_id, func.lower(LandPlot.name) == name.strip().lower())
        return self._db.execute(stmt).scalar_one_or_none()

    def add(self, land_plot: LandPlot) -> None:
        self._db.add(land_plot)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, land_plot: LandPlot) -> None:
        self._db.refresh(land_plot)


class PaddockRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_in_farm(self, farm_id: uuid.UUID, paddock_id: uuid.UUID, *, only_active: bool = False) -> Paddock | None:
        stmt = select(Paddock).where(Paddock.id == paddock_id, Paddock.farm_id == farm_id)
        if only_active:
            stmt = stmt.where(Paddock.is_active.is_(True))
        return self._db.execute(stmt).scalar_one_or_none()

    def list(self, farm_id: uuid.UUID, *, status: str | None = None, land_plot_id: uuid.UUID | None = None) -> list[Paddock]:
        """Potreros activos de la finca, ordenados por lote y nombre (la UI los agrupa)."""
        stmt = (
            select(Paddock)
            .options(joinedload(Paddock.land_plot))
            .join(LandPlot, LandPlot.id == Paddock.land_plot_id)
            .where(Paddock.farm_id == farm_id, Paddock.is_active.is_(True))
            .order_by(LandPlot.name.asc(), Paddock.name.asc())
        )
        if status:
            stmt = stmt.where(Paddock.status == status)
        if land_plot_id:
            stmt = stmt.where(Paddock.land_plot_id == land_plot_id)
        return list(self._db.execute(stmt).scalars().all())

    def first_taken_name(self, farm_id: uuid.UUID, names: Sequence[str]) -> str | None:
        """El primer nombre de la lista que ya usa un potrero de la finca, o None."""
        if not names:
            return None
        stmt = select(Paddock.name).where(Paddock.farm_id == farm_id, Paddock.name.in_(list(names)))
        return self._db.execute(stmt).scalars().first()

    def of_land_plot(self, land_plot_id: uuid.UUID) -> list[Paddock]:
        return list(self._db.execute(select(Paddock).where(Paddock.land_plot_id == land_plot_id)).scalars().all())

    def count_other_active_in_land_plot(self, land_plot_id: uuid.UUID, exclude_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Paddock)
            .where(Paddock.land_plot_id == land_plot_id, Paddock.is_active.is_(True), Paddock.id != exclude_id)
        )
        return int(self._db.execute(stmt).scalar_one())

    def animals_by_paddock(self, paddock_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, list[dict]]:
        """Bovinos activos de cada potrero, en UNA consulta (sin N+1). Modelo de lectura."""
        if not paddock_ids:
            return {}
        bovine: Table = Base.metadata.tables["bovine"]
        rows = self._db.execute(
            select(bovine.c.paddock_id, bovine.c.id, bovine.c.identification_number, bovine.c.name)
            .where(bovine.c.paddock_id.in_(list(paddock_ids)), bovine.c.is_active.is_(True))
            .order_by(bovine.c.identification_number.asc())
        ).all()
        result: dict[uuid.UUID, list[dict]] = {}
        for row in rows:
            result.setdefault(row.paddock_id, []).append(
                {"id": row.id, "identification_number": row.identification_number, "name": row.name}
            )
        return result

    # ── Puertos
    def find_active_ref(self, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> Paddock | None:
        return self.get_in_farm(farm_id, paddock_id, only_active=True)

    def id_by_name(self, farm_id: uuid.UUID, name: str) -> uuid.UUID | None:
        """Id del potrero de la finca con ese nombre (sin distinguir mayúsculas), o None."""
        stmt = select(Paddock.id).where(Paddock.farm_id == farm_id, func.lower(Paddock.name) == name.strip().lower())
        return self._db.execute(stmt).scalar_one_or_none()

    def add(self, paddock: Paddock) -> None:
        self._db.add(paddock)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, paddock: Paddock) -> None:
        self._db.refresh(paddock)
