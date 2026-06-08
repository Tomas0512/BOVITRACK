import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReproductiveEvent(Base):
    __tablename__ = "reproductive_event"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False)
    bovine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="RESTRICT"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bull_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    calf_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    registered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship()
    bovine: Mapped["Bovine"] = relationship(foreign_keys=[bovine_id])
    bull: Mapped["Bovine | None"] = relationship(foreign_keys=[bull_id])
    calf: Mapped["Bovine | None"] = relationship(foreign_keys=[calf_id])
    registrant: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"ReproductiveEvent(id={self.id}, type={self.event_type}, date={self.event_date})"
