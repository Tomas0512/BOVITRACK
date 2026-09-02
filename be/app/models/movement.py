import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Date, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

MOVEMENT_TYPES = {"compra", "venta", "traslado", "nacimiento", "muerte"}


class AnimalMovement(Base):
    __tablename__ = "animal_movement"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    bovine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    animal_identifier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    counterparty_document: Mapped[str | None] = mapped_column(String(50), nullable=True)
    counterparty_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    origin_farm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    destination_farm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship()
    bovine: Mapped["Bovine | None"] = relationship()
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"AnimalMovement(id={self.id}, type={self.movement_type}, bovine={self.bovine_id})"
