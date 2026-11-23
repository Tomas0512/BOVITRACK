"""
Módulo: modules/notifications/dependencies.py (composición del módulo)
¿Qué? Arma un NotificationService por request y conecta sus fuentes de datos:
      planes sanitarios (salud), stock bajo (inventario), miembros y correos
      (identidad) y el envío de email (core).
¿Para qué? Es el módulo con más vecinos; este archivo es el ÚNICO que los conoce.
¿Impacto? Salud e inventario ya son módulos: se usan por su API pública
          (build_sanitary_alerts, build_low_stock_lookup), igual que identidad
          (build_farm_member_lookup, build_user_email_lookup).
"""


import uuid

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import send_generic_email
from app.modules import farms, health, identity, inventory
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.service import NotificationService

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def build_notification_service(db: Session) -> NotificationService:
    """Arma el servicio sobre una sesión dada (la usan el request y la tarea programada)."""
    return NotificationService(
        repository=NotificationRepository(db),
        sanitary_alerts=health.build_sanitary_alerts(db),
        low_stock=inventory.build_low_stock_lookup(db),
        farm_members=identity.build_farm_member_lookup(db),
        user_email=identity.build_user_email_lookup(db),
        send_email=send_generic_email,
    )


def active_farm_ids(db: Session) -> list[uuid.UUID]:
    """Fincas activas que recorre la tarea programada (las responde farms)."""
    return farms.list_active_farm_ids(db)


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependencia de FastAPI: un NotificationService por request."""
    return build_notification_service(db)
