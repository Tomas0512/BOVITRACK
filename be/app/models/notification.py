"""
Módulo: models/notification.py
HU014 - Alertas y notificaciones (Sprint 8 - Tomas)

¿Qué? Modelos ORM para las preferencias de notificación por usuario/finca y el
      historial de notificaciones enviadas.
¿Para qué? Que cada usuario configure su canal (email/in_app) y qué tipo de
           eventos le interesan, y que el sistema guarde un registro de cada
           notificación enviada para mostrar el historial en la web.
¿Impacto? Sin preferencias el motor no sabría a quién ni cómo notificar; sin
          historial no habría trazabilidad de los envíos (idempotencia).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.user import User


class UserNotificationPref(Base):
    """¿Qué? Preferencia de notificación de un usuario dentro de una finca.

    ¿Para qué? Guardar el canal deseado (email/inapp/ambos) y cuáles tipos de
               evento quiere recibir (sanitarios, stock bajo, reproductivos,
               nacimientos) junto con la frecuencia.
    ¿Impacto? Es única por (usuario, finca): una fila por usuario y finca.
    """

    __tablename__ = "user_notification_pref"
    __table_args__ = (
        UniqueConstraint("user_id", "farm_id", name="uq_user_notification_pref"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    notify_sanitary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_low_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_reproductive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_birth: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), default="real_time", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])

    def __repr__(self) -> str:
        return f"UserNotificationPref(user={self.user_id}, farm={self.farm_id}, channel={self.channel})"


class NotificationLog(Base):
    """¿Qué? Registro de una notificación enviada a un usuario (historial).

    ¿Para qué? Mostrar en la web el historial de notificaciones y permitir
               marcar como leída. También sirve para la idempotencia del motor
               (evitar enviar dos veces el mismo evento en la misma ventana).
    ¿Impacto? El usuario puede haber sido eliminado (user_id queda NULL) y el
              registro se conserva igualmente (SET NULL).
    """

    __tablename__ = "notification_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farm.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="sent", nullable=False)
    # Identificador del evento que dispara la notificación (id de plan/food/evento).
    # Sirve como clave de idempotencia para no enviar dos veces el mismo evento.
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])
    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])

    def __repr__(self) -> str:
        return f"NotificationLog(id={self.id}, type={self.type}, status={self.status})"
