"""
Módulo: modules/identity/models/membership.py
¿Qué? Membresía de un usuario en una finca, con el rol que tiene allí (tabla `user_farm`).
¿Para qué? Es la pieza que responde "¿qué puede hacer este usuario en esta finca?".
           require_permission la recorre: membresía activa -> rol activo -> permiso.
¿Impacto? Antes vivía en models/farm.py junto a la finca. Está en identity porque
          los permisos dependen de ella, y identity es la capa base: la membresía
          guarda el farm_id (la llave foránea), pero no navega hacia la finca.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.identity.models.role import Role
    from app.modules.identity.models.user import User


class UserFarm(Base):
    __tablename__ = "user_farm"
    __table_args__ = (UniqueConstraint("user_id", "farm_id", name="uq_user_farm"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("role.id", ondelete="RESTRICT"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    role: Mapped["Role"] = relationship(back_populates="user_farms")
    assigner: Mapped["User | None"] = relationship(foreign_keys=[assigned_by])

    def __repr__(self) -> str:
        return f"UserFarm(user={self.user_id}, farm={self.farm_id})"
