"""
Módulo: modules/notifications/service.py
HU014 - Alertas y notificaciones (Sprint 8 - Tomas)

¿Qué? Motor de alertas y notificaciones de la finca:
      - alertas activas (planes sanitarios vencidos o próximos, insumos en stock bajo);
      - preferencias por usuario y finca (canal, frecuencia, tipos activos);
      - ciclo de notificación idempotente (no repite lo enviado en 24 h);
      - historial, conteo de no leídas y marcar como leída.
¿Para qué? Que la finca no dependa de avisos externos: quien tiene que actuar
           se entera a tiempo, por correo o dentro de la app.
¿Impacto? El banner de alertas y las notificaciones usan la MISMA fuente de
          datos (SanitaryAlertsSource y LowStockLookup), así nunca se contradicen.
          No conoce HTTP, SQLAlchemy ni los modelos de salud, inventario o
          usuarios: todo eso llega por puertos (app.shared.ports).
"""

import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from app.modules.notifications.models import NotificationLog, UserNotificationPref
from app.modules.notifications.repository import NotificationRepository
from app.shared.exceptions import InvalidRequestError, NotFoundError
from app.shared.ports import (
    EmailSender,
    FarmMemberLookup,
    LowStockLookup,
    SanitaryAlertsSource,
    SanitaryDue,
    UserEmailLookup,
)

# Canales y frecuencias válidos.
CHANNELS = frozenset({"email", "in_app", "ambos"})
FREQUENCIES = frozenset({"real_time", "daily", "weekly"})

# Tipos de evento soportados por el motor.
SANITARY_FIELD = "notify_sanitary"
LOW_STOCK_FIELD = "notify_low_stock"
REPRODUCTIVE_FIELD = "notify_reproductive"
BIRTH_FIELD = "notify_birth"

# Tipo -> campo de preferencia que activa la notificación.
NOTIFY_FIELD_BY_TYPE = {
    "sanitary": SANITARY_FIELD,
    "low_stock": LOW_STOCK_FIELD,
    "reproductive": REPRODUCTIVE_FIELD,
    "birth": BIRTH_FIELD,
}

# Título humano para cada tipo.
TYPE_LABELS = {
    "sanitary": "Sanitario",
    "low_stock": "Stock bajo",
    "reproductive": "Reproductivo",
    "birth": "Nacimiento",
}

DEDUP_WINDOW_HOURS = 24
NOTIFICATION_NOT_FOUND = "Notificación no encontrada o no pertenece al usuario"


# ── Reglas puras (sin estado ni dependencias) ──────────────────


def _pref_allows(pref: UserNotificationPref, notif_type: str) -> bool:
    """¿La preferencia activa el envío para este tipo? Tipos no mapeados: sí, por defecto."""
    field = NOTIFY_FIELD_BY_TYPE.get(notif_type)
    if field is None:
        return True
    return bool(getattr(pref, field, False))


def _notify_channel(pref: UserNotificationPref) -> tuple[bool, bool]:
    """(envía_email, guarda_in_app) según el canal elegido."""
    if pref.channel == "email":
        return True, False
    if pref.channel == "in_app":
        return False, True
    return True, True  # ambos


def _log_channel(send_email: bool, log_in_app: bool) -> str:
    """Canal efectivo que queda registrado en el historial."""
    if send_email and log_in_app:
        return "ambos"
    return "email" if send_email else "in_app"


def _target_label(bovine_id: uuid.UUID | None) -> str:
    return f"Bovino #{str(bovine_id)[:8]}" if bovine_id else "Lote"


def _iso(value: Any) -> str | None:
    return value.isoformat() if value else None


def _plan_alert(plan: SanitaryDue) -> dict[str, Any]:
    """Un plan sanitario como lo muestra el banner de alertas."""
    return {
        "id": str(plan.id),
        "vaccine_or_treatment_name": plan.vaccine_or_treatment_name,
        "treatment_type": plan.treatment_type,
        "next_scheduled_date": _iso(plan.next_scheduled_date),
        "bovine_id": str(plan.bovine_id) if plan.bovine_id else None,
        "land_plot_id": str(plan.land_plot_id) if plan.land_plot_id else None,
    }


class NotificationService:
    """Casos de uso del módulo de alertas y notificaciones."""

    def __init__(
        self,
        repository: NotificationRepository,
        sanitary_alerts: SanitaryAlertsSource,
        low_stock: LowStockLookup,
        farm_members: FarmMemberLookup,
        user_email: UserEmailLookup,
        send_email: EmailSender,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repo = repository
        self._sanitary = sanitary_alerts
        self._low_stock = low_stock
        self._members = farm_members
        self._user_email = user_email
        self._send_email = send_email
        self._now = now

    # ── Alertas activas (banner) ─────────────────────────────

    def active_alerts(self, farm_id: uuid.UUID, days: int = 7) -> dict[str, list[dict[str, Any]]]:
        """Planes vencidos, planes de los próximos `days` días e insumos en stock bajo."""
        now = self._now()
        until = now + timedelta(days=days)
        return {
            "overdue": [_plan_alert(p) for p in self._sanitary.overdue(farm_id, now)],
            "upcoming": [_plan_alert(p) for p in self._sanitary.upcoming(farm_id, now, until)],
            "low_stock": [
                {
                    "id": str(f.id),
                    "name": f.name,
                    "category": f.category,
                    "current_stock": float(f.current_stock),
                    "min_stock_alert": float(f.min_stock_alert) if f.min_stock_alert else None,
                    "unit_of_measure": f.unit_of_measure,
                }
                for f in self._low_stock(farm_id)
            ],
        }

    def build_alert_candidates(self, farm_id: uuid.UUID, days: int = 7) -> list[dict[str, str]]:
        """Eventos que merecen notificación, con título y mensaje listos para enviar."""
        now = self._now()
        until = now + timedelta(days=days)
        candidates: list[dict[str, str]] = []
        for plan in self._sanitary.overdue(farm_id, now):
            candidates.append({
                "type": "sanitary",
                "subcategory": "overdue",
                "reference_id": str(plan.id),
                "title": f"Plan sanitario vencido: {plan.vaccine_or_treatment_name}",
                "message": f"{plan.vaccine_or_treatment_name} para {_target_label(plan.bovine_id)} venció el "
                f"{_iso(plan.next_scheduled_date) or '—'}.",
            })
        for plan in self._sanitary.upcoming(farm_id, now, until):
            candidates.append({
                "type": "sanitary",
                "subcategory": "upcoming",
                "reference_id": str(plan.id),
                "title": f"Plan sanitario próximo: {plan.vaccine_or_treatment_name}",
                "message": f"{plan.vaccine_or_treatment_name} para {_target_label(plan.bovine_id)} está programado para el "
                f"{_iso(plan.next_scheduled_date) or '—'}.",
            })
        for food in self._low_stock(farm_id):
            candidates.append({
                "type": "low_stock",
                "subcategory": "low_stock",
                "reference_id": str(food.id),
                "title": f"Stock bajo: {food.name}",
                "message": f"El insumo {food.name} tiene {food.current_stock} {food.unit_of_measure} "
                f"y su mínimo es {food.min_stock_alert} {food.unit_of_measure}.",
            })
        return candidates

    # ── Preferencias ─────────────────────────────────────────

    def get_or_create_prefs(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> UserNotificationPref:
        """Preferencia del usuario en la finca; si no existe se crea con valores por defecto."""
        pref = self._repo.get_prefs(user_id, farm_id)
        if pref is None:
            pref = UserNotificationPref(
                user_id=user_id,
                farm_id=farm_id,
                channel="email",
                notify_sanitary=True,
                notify_low_stock=True,
                notify_reproductive=True,
                notify_birth=True,
                frequency="real_time",
            )
            self._repo.add(pref)
            self._repo.commit()
            self._repo.refresh(pref)
        return pref

    def update_prefs(
        self,
        user_id: uuid.UUID,
        farm_id: uuid.UUID,
        *,
        channel: str | None = None,
        notify_sanitary: bool | None = None,
        notify_low_stock: bool | None = None,
        notify_reproductive: bool | None = None,
        notify_birth: bool | None = None,
        frequency: str | None = None,
    ) -> UserNotificationPref:
        """Actualiza solo lo enviado. Un False desactiva el tipo (no se confunde con None)."""
        pref = self.get_or_create_prefs(user_id, farm_id)
        if channel is not None:
            if channel not in CHANNELS:
                raise InvalidRequestError(f"Canal inválido: {channel}. Usa uno de {sorted(CHANNELS)}")
            pref.channel = channel
        if frequency is not None:
            if frequency not in FREQUENCIES:
                raise InvalidRequestError(f"Frecuencia inválida: {frequency}. Usa una de {sorted(FREQUENCIES)}")
            pref.frequency = frequency
        if notify_sanitary is not None:
            pref.notify_sanitary = notify_sanitary
        if notify_low_stock is not None:
            pref.notify_low_stock = notify_low_stock
        if notify_reproductive is not None:
            pref.notify_reproductive = notify_reproductive
        if notify_birth is not None:
            pref.notify_birth = notify_birth
        self._repo.commit()
        self._repo.refresh(pref)
        return pref

    # ── Ciclo de notificación ────────────────────────────────

    def _already_sent(self, user_id: uuid.UUID, notif_type: str, reference_id: str) -> bool:
        since = self._now() - timedelta(hours=DEDUP_WINDOW_HOURS)
        return self._repo.exists_since(user_id, notif_type, reference_id, since)

    async def run_notification_cycle(self, farm_id: uuid.UUID, days: int = 7) -> int:
        """Genera y envía lo pendiente para cada miembro activo. Devuelve cuántas creó.

        Idempotente: una misma alerta no se repite al mismo usuario en 24 h.
        """
        candidates = self.build_alert_candidates(farm_id, days=days)
        if not candidates:
            return 0
        members = self._members(farm_id)
        created = 0
        for candidate in candidates:
            notif_type = candidate["type"]
            reference_id = candidate["reference_id"]
            for member_id in members:
                pref = self.get_or_create_prefs(member_id, farm_id)
                if not _pref_allows(pref, notif_type):
                    continue
                if self._already_sent(member_id, notif_type, reference_id):
                    continue
                send_email, log_in_app = _notify_channel(pref)
                self._repo.add(NotificationLog(
                    farm_id=farm_id,
                    user_id=member_id,
                    type=notif_type,
                    title=candidate["title"],
                    message=candidate["message"],
                    channel=_log_channel(send_email, log_in_app),
                    status="sent",
                    reference_id=reference_id,
                    sent_at=self._now(),
                ))
                self._repo.flush()
                created += 1
                if send_email:
                    email = self._user_email(member_id)
                    if email:
                        await self._send_email(
                            to_email=email,
                            subject=f"BoviTrack — {candidate['title']}",
                            body_html=(
                                f"<h2 style='color:#2D6A4F;'>Alerta BoviTrack</h2>"
                                f"<p style='color:#374151;'>{candidate['message']}</p>"
                            ),
                            label="NOTIFICACIÓN",
                        )
        self._repo.commit()
        return created

    # ── Historial ────────────────────────────────────────────

    def list_notification_history(
        self,
        user_id: uuid.UUID,
        farm_id: uuid.UUID,
        *,
        notif_type: str | None = None,
        unread_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotificationLog]:
        return self._repo.list_history(
            user_id, farm_id, notif_type=notif_type, unread_only=unread_only, limit=limit, offset=offset
        )

    def count_notification_history(
        self, user_id: uuid.UUID, farm_id: uuid.UUID, *, notif_type: str | None = None, unread_only: bool = False
    ) -> int:
        """Total real del historial (con filtros), para paginar en el frontend."""
        return self._repo.count_history(user_id, farm_id, notif_type=notif_type, unread_only=unread_only)

    def count_unread_notifications(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> int:
        """Conteo para la campana. NO ejecuta el motor (no envía correos)."""
        return self._repo.count_unread(user_id, farm_id)

    def mark_as_read(self, user_id: uuid.UUID, farm_id: uuid.UUID, log_id: uuid.UUID) -> None:
        """Marca la notificación como leída. NotFoundError si no es del usuario en esa finca."""
        log = self._repo.get_log_for_user(user_id, farm_id, log_id)
        if log is None:
            raise NotFoundError(NOTIFICATION_NOT_FOUND)
        log.read_at = self._now()
        self._repo.commit()
