import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MilkProduction(Base):
    __tablename__ = "milk_production"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    bovine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    land_plot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("land_plot.id", ondelete="SET NULL"), nullable=True)
    milking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quantity_liters: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    milking_type: Mapped[str] = mapped_column(String(20), nullable=False)
    milking_session: Mapped[str | None] = mapped_column(String(20), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship()
    bovine: Mapped["Bovine | None"] = relationship()
    land_plot: Mapped["LandPlot | None"] = relationship()
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"MilkProduction(id={self.id}, liters={self.quantity_liters})"
