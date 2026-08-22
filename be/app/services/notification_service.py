"""
Módulo: services/notification_service.py
HU014 - Alertas y notificaciones (Sprint 8 - Tomas)

¿Qué? Lógica de negocio del motor de notificaciones: preferencias por
      usuario/finca, generación de candidatos de alerta a partir de los datos
      existentes (planes sanitarios, inventario) y envío idempotente de
      notificaciones con registro en historial.
¿Para qué? Que cada usuario configure qué/cómo notificarse, y que el sistema
           cree el historial de notificaciones sin duplicar envíos.
¿Impacto? Centraliza la generación de alertas reutilizando la misma fuente de
          datos que el endpoint de alertas, de modo que banner y notificaciones
          nunca se contradigan.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import UserFarm
from app.models.food import Food
from app.models.notification import NotificationLog, UserNotificationPref
from app.models.sanitary_plan import SanitaryPlan
from app.models.user import User
from app.utils.email import send_generic_email

# Canales y frecuencias válidos.
CHANNELS = frozenset({"email", "in_app", "ambos"})
FREQUENCIES = frozenset({"real_time", "daily", "weekly"})

# Tipos de evento soportados por el motor.
SANITARY_FIELD = "notify_sanitary"
LOW_STOCK_FIELD = "notify_low_stock"
REPRODUCTIVE_FIELD = "notify_reproductive"
BIRTH_FIELD = "notify_birth"

# Tipo → campo de preferencia que activa la notificación.
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


def get_or_create_prefs(
    db: Session, user_id: uuid.UUID, farm_id: uuid.UUID
) -> UserNotificationPref:
    """¿Qué? Devuelve la preferencia del usuario para la finca, creándola si no existe.

    ¿Para qué? Que el endpoint GET no falle si el usuario nunca configuró nada.
    ¿Impacto? Aplica los valores por defecto (email, todos los tipos, real_time).
    """
    stmt = select(UserNotificationPref).where(
        UserNotificationPref.user_id == user_id,
        UserNotificationPref.farm_id == farm_id,
    )
    pref = db.execute(stmt).scalar_one_or_none()
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
        db.add(pref)
        db.flush()
    return pref


def update_prefs(
    db: Session,
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
    """¿Qué? Actualiza las preferencias del usuario para la finca.

    ¿Para qué? Guardar la configuración que el usuario hace desde la web.
    ¿Impacto? Solo cambia los campos enviados; valida canal y frecuencia.
              Los booleanos de tipo se tratan con cuidado para permitir False.
    """
    pref = get_or_create_prefs(db, user_id, farm_id)

    if channel is not None:
        if channel not in CHANNELS:
            raise ValueError(f"Canal inválido: {channel}. Usa uno de {sorted(CHANNELS)}")
        pref.channel = channel

    if frequency is not None:
        if frequency not in FREQUENCIES:
            raise ValueError(f"Frecuencia inválida: {frequency}. Usa una de {sorted(FREQUENCIES)}")
        pref.frequency = frequency

    if notify_sanitary is not None:
        pref.notify_sanitary = notify_sanitary
    if notify_low_stock is not None:
        pref.notify_low_stock = notify_low_stock
    if notify_reproductive is not None:
        pref.notify_reproductive = notify_reproductive
    if notify_birth is not None:
        pref.notify_birth = notify_birth

    db.flush()
    return pref


def build_alert_candidates(db: Session, farm_id: uuid.UUID, days: int = 7) -> list[dict]:
    """¿Qué? Genera los eventos candidatos de alerta para la finca.

    ¿Para qué? Alimentar al motor de notificaciones con la misma fuente de
               datos que usa el endpoint de alertas (planes sanitarios
               vencidos/próximos + alimentos en stock bajo).
    ¿Impacto? Devuelve una lista de dicts normalizados (type, reference_id,
              title, message) lista para enviar.
    """
    candidates: list[dict] = []
    now = datetime.now()
    window = now + timedelta(days=days)

    # Planes sanitarios VENCIDOS.
    overdue_stmt = select(SanitaryPlan).where(
        SanitaryPlan.farm_id == farm_id,
        SanitaryPlan.is_active.is_(True),
        SanitaryPlan.next_scheduled_date < now,
    )
    for plan in db.execute(overdue_stmt).scalars().all():
        target = f"Bovino #{str(plan.bovine_id)[:8]}" if plan.bovine_id else "Lote"
        candidates.append(
            {
                "type": "sanitary",
                "subcategory": "overdue",
                "reference_id": str(plan.id),
                "title": f"Plan sanitario vencido: {plan.vaccine_or_treatment_name}",
                "message": f"{plan.vaccine_or_treatment_name} para {target} venció el "
                f"{plan.next_scheduled_date.isoformat() if plan.next_scheduled_date else '—'}.",
            }
        )

    # Planes sanitarios PRÓXIMOS (dentro de la ventana).
    upcoming_stmt = select(SanitaryPlan).where(
        SanitaryPlan.farm_id == farm_id,
        SanitaryPlan.is_active.is_(True),
        SanitaryPlan.next_scheduled_date >= now,
        SanitaryPlan.next_scheduled_date <= window,
    )
    for plan in db.execute(upcoming_stmt).scalars().all():
        target = f"Bovino #{str(plan.bovine_id)[:8]}" if plan.bovine_id else "Lote"
        candidates.append(
            {
                "type": "sanitary",
                "subcategory": "upcoming",
                "reference_id": str(plan.id),
                "title": f"Plan sanitario próximo: {plan.vaccine_or_treatment_name}",
                "message": f"{plan.vaccine_or_treatment_name} para {target} está programado para el "
                f"{plan.next_scheduled_date.isoformat() if plan.next_scheduled_date else '—'}.",
            }
        )

    # Alimentos en stock bajo.
    low_stmt = select(Food).where(
        Food.farm_id == farm_id,
        Food.is_active.is_(True),
        Food.min_stock_alert.isnot(None),
        Food.current_stock <= Food.min_stock_alert,
    )
    for food in db.execute(low_stmt).scalars().all():
        candidates.append(
            {
                "type": "low_stock",
                "subcategory": "low_stock",
                "reference_id": str(food.id),
                "title": f"Stock bajo: {food.name}",
                "message": f"El insumo {food.name} tiene {food.current_stock} {food.unit_of_measure} "
                f"y su mínimo es {food.min_stock_alert} {food.unit_of_measure}.",
            }
        )

    return candidates


def _pref_allows(pref: UserNotificationPref, notif_type: str) -> bool:
    """¿Qué? Dice si la preferencia activa el envío para un tipo de evento."""
    field = NOTIFY_FIELD_BY_TYPE.get(notif_type)
    if field is None:
        return True
    return bool(getattr(pref, field, False))


def _already_sent(
    db: Session, user_id: uuid.UUID, notif_type: str, reference_id: str, hours: int = 24
) -> bool:
    """¿Qué? Determina si ya se envió una notificación idéntica en la ventana.

    ¿Para qué? Idempotencia: no duplicar envíos del mismo evento.
    ¿Impacto? Se consideran duplicados los logs del mismo tipo+referencia al
              mismo usuario dentro de las últimas `hours` horas.
    """
    threshold = datetime.now() - timedelta(hours=hours)
    stmt = select(NotificationLog.id).where(
        NotificationLog.user_id == user_id,
        NotificationLog.type == notif_type,
        NotificationLog.reference_id == reference_id,
        NotificationLog.created_at >= threshold,
    )
    return db.execute(stmt).scalars().first() is not None


def _notify_channel(pref: UserNotificationPref) -> tuple[bool, bool]:
    """¿Qué? Determina si se envía por email y/o se guarda como in_app.

    Devuelve (envia_email, guarda_in_app).
    """
    if pref.channel == "email":
        return True, False
    if pref.channel == "in_app":
        return False, True
    return True, True  # ambos


async def run_notification_cycle(db: Session, farm_id: uuid.UUID, days: int = 7) -> int:
    """¿Qué? Genera y envía las notificaciones pendientes para la finca.

    ¿Para qué? Ejecutar el motor de notificaciones de forma idempotente: copia
               de seguridad y deuda (una llamada repetida no duplica envíos).
    ¿Impacto? Para cada miembro activo de la finca crea el NotificationLog y,
              si su canal lo permite, envía el correo. Retorna cuántas
              notificaciones nuevas se generaron.
    """
    candidates = build_alert_candidates(db, farm_id, days=days)
    if not candidates:
        return 0

    members = db.execute(
        select(UserFarm).where(
            UserFarm.farm_id == farm_id,
            UserFarm.is_active.is_(True),
        )
    ).scalars().all()

    created = 0
    for candidate in candidates:
        notif_type = candidate["type"]
        reference_id = candidate["reference_id"]

        for uf in members:
            pref = get_or_create_prefs(db, uf.user_id, farm_id)
            if not _pref_allows(pref, notif_type):
                continue
            if _already_sent(db, uf.user_id, notif_type, reference_id):
                continue

            send_email, log_in_app = _notify_channel(pref)

            # Canal efectivo registrado en el historial.
            if send_email and log_in_app:
                log_channel = "ambos"
            elif send_email:
                log_channel = "email"
            else:
                log_channel = "in_app"

            log = NotificationLog(
                farm_id=farm_id,
                user_id=uf.user_id,
                type=notif_type,
                title=candidate["title"],
                message=candidate["message"],
                channel=log_channel,
                status="sent",
                reference_id=reference_id,
                sent_at=datetime.now(),
            )
            db.add(log)
            db.flush()
            created += 1

            if send_email:
                user = db.get(User, uf.user_id)
                if user and user.email:
                    await send_generic_email(
                        to_email=user.email,
                        subject=f"BoviTrack — {candidate['title']}",
                        body_html=(
                            f"<h2 style='color:#2D6A4F;'>Alerta BoviTrack</h2>"
                            f"<p style='color:#374151;'>{candidate['message']}</p>"
                        ),
                        label="NOTIFICACIÓN",
                    )

    db.commit()
    return created


def list_notification_history(
    db: Session,
    user_id: uuid.UUID,
    farm_id: uuid.UUID,
    *,
    notif_type: str | None = None,
    unread_only: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> list[NotificationLog]:
    """¿Qué? Historial de notificaciones del usuario en la finca (filtrable).

    ¿Para qué? Mostrar en la web el historial y permitir filtrar por tipo.
    ¿Impacto? Devuelve los logs del usuario; si unread_only, solo los no leídos.
    """
    stmt = select(NotificationLog).where(
        NotificationLog.user_id == user_id,
        NotificationLog.farm_id == farm_id,
    )
    if notif_type:
        stmt = stmt.where(NotificationLog.type == notif_type)
    if unread_only:
        stmt = stmt.where(NotificationLog.read_at.is_(None))

    stmt = stmt.order_by(NotificationLog.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


def mark_as_read(db: Session, user_id: uuid.UUID, farm_id: uuid.UUID, log_id: uuid.UUID) -> bool:
    """¿Qué? Marca una notificación como leída (si pertenece al usuario).

    ¿Para qué? Permitir al usuario cerrar/confirmar notificaciones.
    ¿Impacto? Solo afecta al log indicado; retorna True si se actualizó.
    """
    stmt = select(NotificationLog).where(
        NotificationLog.id == log_id,
        NotificationLog.user_id == user_id,
        NotificationLog.farm_id == farm_id,
    )
    log = db.execute(stmt).scalar_one_or_none()
    if log is None:
        return False
    log.read_at = datetime.now()
    db.commit()
    return True
