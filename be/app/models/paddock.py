import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Paddock(Base):
    __tablename__ = "paddock"
    __table_args__ = (UniqueConstraint("farm_id", "name", name="uq_paddock_farm_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area_hectares: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    coverage_status: Mapped[str] = mapped_column(String(30), default="bueno", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="libre", nullable=False)
    rest_start_date = mapped_column(Date, nullable=True)
    rest_end_date = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship(back_populates="paddocks")
    herd_assignments: Mapped[list["PaddockHerd"]] = relationship(back_populates="paddock", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Paddock(id={self.id}, name={self.name})"


class PaddockHerd(Base):
    __tablename__ = "paddock_herd"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paddock_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("paddock.id", ondelete="CASCADE"), nullable=False)
    land_plot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_plot.id", ondelete="CASCADE"), nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    animal_count: Mapped[int] = mapped_column(Integer, nullable=False)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    paddock: Mapped["Paddock"] = relationship(back_populates="herd_assignments")
    land_plot: Mapped["LandPlot"] = relationship()
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"PaddockHerd(id={self.id}, paddock={self.paddock_id})"
