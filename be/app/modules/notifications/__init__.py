"""
Módulo notifications — API pública (alertas y notificaciones, HU014).

`api_router` y `start_notification_scheduler` se cargan solo cuando se piden
(mismo patrón que los demás módulos: no arrastrar capas al registrar el modelo).
"""

from typing import TYPE_CHECKING, Any

from app.modules.notifications.schemas import NotificationLogResponse, UnreadCountResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter
    from app.modules.notifications.scheduler import start_notification_scheduler

__all__ = ["NotificationLogResponse", "UnreadCountResponse", "api_router", "start_notification_scheduler"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.notifications.router import router

        return router
    if name == "start_notification_scheduler":
        from app.modules.notifications.scheduler import start_notification_scheduler

        return start_notification_scheduler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
