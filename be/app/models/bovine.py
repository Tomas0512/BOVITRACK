import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Bovine(Base):
    __tablename__ = "bovine"
    __table_args__ = (UniqueConstraint("farm_id", "identification_number", name="uq_bovine_farm_ident"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    land_plot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("land_plot.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    identification_number: Mapped[str] = mapped_column(String(50), nullable=False)
    sex: Mapped[str] = mapped_column(String(10), nullable=False)
    breed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    markings: Mapped[str | None] = mapped_column(Text, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    current_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    father_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    mother_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="activo", nullable=False)
    entry_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exit_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship(back_populates="bovines")
    land_plot: Mapped["LandPlot | None"] = relationship()
    father: Mapped["Bovine | None"] = relationship(foreign_keys=[father_id], remote_side="Bovine.id")
    mother: Mapped["Bovine | None"] = relationship(foreign_keys=[mother_id], remote_side="Bovine.id")
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])
    identifications: Mapped[list["BovineIdentification"]] = relationship(back_populates="bovine", cascade="all, delete-orphan")
    audits: Mapped[list["BovineAudit"]] = relationship(back_populates="bovine")

    def __repr__(self) -> str:
        return f"Bovine(id={self.id}, ident={self.identification_number})"


class BovineIdentification(Base):
    __tablename__ = "bovine_identification"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bovine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="CASCADE"), nullable=False)
    id_type: Mapped[str] = mapped_column(String(50), nullable=False)
    id_value: Mapped[str] = mapped_column(String(100), nullable=False)
    body_location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    applied_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bovine: Mapped["Bovine"] = relationship(back_populates="identifications")

    def __repr__(self) -> str:
        return f"BovineIdentification(id={self.id}, type={self.id_type})"


class BovineAudit(Base):
    __tablename__ = "bovine_audit"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bovine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="RESTRICT"), nullable=False)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    field_changed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bovine: Mapped["Bovine"] = relationship(back_populates="audits")
    farm: Mapped["Farm"] = relationship()
    performer: Mapped["User"] = relationship(foreign_keys=[performed_by])

    def __repr__(self) -> str:
        return f"BovineAudit(id={self.id}, bovine={self.bovine_id}, action={self.action})"
