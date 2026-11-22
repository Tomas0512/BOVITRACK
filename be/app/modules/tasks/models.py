"""
Módulo: modules/tasks/models.py
¿Qué? Tabla ORM `task`: una tarea operativa asignada a un miembro de la finca.
¿Para qué? Persistir quién asigna, quién ejecuta, para cuándo y en qué estado está.
¿Impacto? Solo el repositorio de este módulo consulta esta tabla. La vista SQL
          v_pending_tasks (módulo de reportes) también la lee directamente.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    # Solo para el chequeo de tipos: en ejecución SQLAlchemy resuelve las
    # relaciones por nombre ("Farm", "User"...), sin importar esos modelos.
    from app.modules.livestock.models import Bovine
    from app.modules.farms.models import Farm, LandPlot
    from app.modules.identity.models import User


class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False)
    assigned_to: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assigned_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="media", nullable=False)
    bovine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bovine.id", ondelete="SET NULL"), nullable=True)
    land_plot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("land_plot.id", ondelete="SET NULL"), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm: Mapped["Farm"] = relationship()
    assignee: Mapped["User"] = relationship(foreign_keys=[assigned_to])
    assigner: Mapped["User"] = relationship(foreign_keys=[assigned_by])
    bovine: Mapped["Bovine | None"] = relationship()
    land_plot: Mapped["LandPlot | None"] = relationship()

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title})"
