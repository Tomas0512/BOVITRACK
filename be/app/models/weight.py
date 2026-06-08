import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Weight(Base):
    """
    Tabla: weight
    ¿Qué? Historial de pesajes de un bovino.
    ¿Para qué? Registrar cada pesaje individual con fecha para poder
               calcular la ganancia diaria y graficar la evolución de peso.
    ¿Impacto? Reemplaza el campo estático current_weight del bovino
              como fuente de historial. El campo current_weight del bovino
              se actualiza en el servicio al registrar un nuevo pesaje.
    """
    __tablename__ = "weight"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    bovine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="CASCADE"), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    measured_at: Mapped[date] = mapped_column(Date, nullable=False)
    daily_gain: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)   # calculado en el service
    body_condition: Mapped[int | None] = mapped_column(Integer, nullable=True)          # escala 1-5
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    synchronized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship()
    bovine: Mapped["Bovine"] = relationship(back_populates="weights")
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"Weight(id={self.id}, bovine={self.bovine_id}, kg={self.weight_kg})"
