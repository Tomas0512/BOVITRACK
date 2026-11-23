"""
Módulo: modules/farms/models/farm.py
¿Qué? La finca (tabla `farm`) y sus lotes (`land_plot`).
¿Para qué? Es la unidad de trabajo de toda la app: casi todas las tablas
           guardan un farm_id.
¿Impacto? La finca no navega hacia el ganado ni hacia otros módulos: farms está
          por DEBAJO de ellos. Solo conoce a identity (dueño y membresías).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.farms.models.department import Department
    from app.modules.farms.models.paddock import Paddock
    from app.modules.farms.models.purpose import Purpose
    from app.modules.identity.models import User, UserFarm


class Farm(Base):
    __tablename__ = "farm"
    __table_args__ = (UniqueConstraint("name", "department_id", "city_municipality", name="uq_farm_name_location"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("department.id", ondelete="RESTRICT"), nullable=False)
    city_municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    total_area: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    area_unit: Mapped[str] = mapped_column(String(20), default="hectareas", nullable=False)
    purpose_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purpose.id", ondelete="RESTRICT"), nullable=False)
    farm_identifier: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    department: Mapped["Department"] = relationship()
    purpose: Mapped["Purpose"] = relationship()
    # Membresías (identity). Solo en este sentido: identity no conoce las fincas.
    user_farms: Mapped[list["UserFarm"]] = relationship(cascade="all, delete-orphan")
    land_plots: Mapped[list["LandPlot"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    paddocks: Mapped[list["Paddock"]] = relationship(back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Farm(id={self.id}, name={self.name})"


class LandPlot(Base):
    __tablename__ = "land_plot"
    __table_args__ = (UniqueConstraint("farm_id", "name", name="uq_land_plot_farm_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    area_unit: Mapped[str] = mapped_column(String(20), default="hectareas", nullable=False)
    usage_type: Mapped[str] = mapped_column(String(50), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship(back_populates="land_plots")

    def __repr__(self) -> str:
        return f"LandPlot(id={self.id}, name={self.name})"
