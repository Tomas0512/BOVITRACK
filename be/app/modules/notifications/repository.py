"""
Módulo: modules/notifications/repository.py
¿Qué? Acceso a datos de las tablas `user_notification_pref` (preferencias por
      usuario y finca) y `notification_log` (historial de notificaciones).
¿Para qué? Que el servicio pregunte "¿ya se notificó esto en las últimas 24 h?"
           o "¿cuántas tengo sin leer?" sin escribir consultas.
¿Impacto? Toda consulta del historial filtra por usuario Y finca: nadie ve ni
          marca como leídas notificaciones ajenas.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.notifications.models import NotificationLog, UserNotificationPref


class NotificationRepository:
    """Repositorio de preferencias e historial de notificaciones."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Preferencias ─────────────────────────────────────────

    def get_prefs(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> UserNotificationPref | None:
        stmt = select(UserNotificationPref).where(
            UserNotificationPref.user_id == user_id,
            UserNotificationPref.farm_id == farm_id,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    # ── Historial ────────────────────────────────────────────

    def exists_since(self, user_id: uuid.UUID, notif_type: str, reference_id: str, since: datetime) -> bool:
        """¿Ya hay una notificación igual (usuario, tipo, referencia) desde `since`?"""
        stmt = select(NotificationLog.id).where(
            NotificationLog.user_id == user_id,
            NotificationLog.type == notif_type,
            NotificationLog.reference_id == reference_id,
            NotificationLog.created_at >= since,
        )
        return self._db.execute(stmt).scalars().first() is not None

    @staticmethod
    def _history_filters(
        stmt: Any, user_id: uuid.UUID, farm_id: uuid.UUID, notif_type: str | None, unread_only: bool
    ) -> Any:
        stmt = stmt.where(NotificationLog.user_id == user_id, NotificationLog.farm_id == farm_id)
        if notif_type:
            stmt = stmt.where(NotificationLog.type == notif_type)
        if unread_only:
            stmt = stmt.where(NotificationLog.read_at.is_(None))
        return stmt

    def count_history(
        self, user_id: uuid.UUID, farm_id: uuid.UUID, *, notif_type: str | None = None, unread_only: bool = False
    ) -> int:
        """Total del historial con los mismos filtros, sin paginar."""
        stmt = self._history_filters(select(func.count(NotificationLog.id)), user_id, farm_id, notif_type, unread_only)
        return int(self._db.execute(stmt).scalar() or 0)

    def list_history(
        self,
        user_id: uuid.UUID,
        farm_id: uuid.UUID,
        *,
        notif_type: str | None = None,
        unread_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotificationLog]:
        stmt = self._history_filters(select(NotificationLog), user_id, farm_id, notif_type, unread_only)
        stmt = stmt.order_by(NotificationLog.created_at.desc()).limit(limit).offset(offset)
        return list(self._db.execute(stmt).scalars().all())

    def count_unread(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> int:
        stmt = select(func.count(NotificationLog.id)).where(
            NotificationLog.user_id == user_id,
            NotificationLog.farm_id == farm_id,
            NotificationLog.read_at.is_(None),
        )
        return int(self._db.execute(stmt).scalar() or 0)

    def get_log_for_user(
        self, user_id: uuid.UUID, farm_id: uuid.UUID, log_id: uuid.UUID
    ) -> NotificationLog | None:
        stmt = select(NotificationLog).where(
            NotificationLog.id == log_id,
            NotificationLog.user_id == user_id,
            NotificationLog.farm_id == farm_id,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    # ── Unidad de trabajo ────────────────────────────────────

    def add(self, row: UserNotificationPref | NotificationLog) -> None:
        self._db.add(row)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, row: UserNotificationPref | NotificationLog) -> None:
        self._db.refresh(row)
