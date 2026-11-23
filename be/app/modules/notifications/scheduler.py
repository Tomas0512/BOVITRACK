"""
Módulo: modules/notifications/scheduler.py (tarea programada)
¿Qué? Cada NOTIFICATIONS_INTERVAL_MINUTES recorre todas las fincas activas y
      ejecuta el ciclo de notificación de cada una.
¿Para qué? Que los avisos salgan solos, a tiempo, sin depender de que alguien
           abra la pantalla de alertas. Antes GET /alerts/history disparaba el
           motor y podía enviar correos solo por consultar.
¿Impacto? - Cada finca usa su propia sesión: si una falla, se registra el error
            y se sigue con las demás.
          - El motor es idempotente (24 h), así que si hay varios procesos del
            backend corriendo la tarea a la vez, no se duplican los avisos.
          - Arranca y se detiene con la app (lifespan en app/main.py).
"""

import asyncio
import logging
import uuid
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.notifications.dependencies import active_farm_ids, build_notification_service

logger = logging.getLogger(__name__)

INITIAL_DELAY_SECONDS = 30


async def run_cycle_for_all_farms(session_factory: Callable[[], Session] = SessionLocal) -> int:
    """Ejecuta el ciclo en cada finca activa. Devuelve cuántas notificaciones creó en total."""
    db = session_factory()
    try:
        farm_ids: list[uuid.UUID] = active_farm_ids(db)
    finally:
        db.close()

    created = 0
    for farm_id in farm_ids:
        db = session_factory()
        try:
            created += await build_notification_service(db).run_notification_cycle(farm_id)
        except Exception:  # noqa: BLE001 — una finca con error no detiene a las demás
            db.rollback()
            logger.exception("Error en el ciclo de notificaciones de la finca %s", farm_id)
        finally:
            db.close()
    return created


async def _notification_loop(interval_minutes: int) -> None:
    await asyncio.sleep(INITIAL_DELAY_SECONDS)
    while True:
        try:
            created = await run_cycle_for_all_farms()
            if created:
                logger.info("🔔 Ciclo de notificaciones: %s nuevas", created)
        except Exception:  # noqa: BLE001 — la tarea nunca debe morir por un error puntual
            logger.exception("Error en la tarea programada de notificaciones")
        await asyncio.sleep(interval_minutes * 60)


def start_notification_scheduler(interval_minutes: int) -> asyncio.Task[None] | None:
    """Arranca la tarea en el event loop actual. Con intervalo <= 0 no hace nada."""
    if interval_minutes <= 0:
        logger.info("🔕 Tarea programada de notificaciones desactivada")
        return None
    logger.info("🔔 Tarea programada de notificaciones cada %s min", interval_minutes)
    return asyncio.create_task(_notification_loop(interval_minutes))
