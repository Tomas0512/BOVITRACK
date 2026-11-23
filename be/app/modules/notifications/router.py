"""
Módulo: modules/notifications/router.py (frontera HTTP del módulo)
¿Qué? Router para alertas sanitarias, de inventario y notificaciones (HU014).
¿Para qué? Endpoint unificado de alertas próximas/vencidas, preferencias de
           notificación por usuario y historial de notificaciones.
¿Impacto? Integración con frontend para mostrar AlertBanner, configurar las
          preferencias y consultar el historial.
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.notifications.dependencies import (
    get_current_user,
    get_notification_service,
    require_permission,
)

from app.modules.notifications.schemas import (
    NotificationHistoryResponse,
    NotificationLogResponse,
    NotificationPrefResponse,
    NotificationPrefUpdate,
    UnreadCountResponse,
)
from app.modules.notifications.service import NotificationService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/alerts", tags=["Alertas"])


@router.get("", summary="Obtener alertas activas de la finca",
            dependencies=[Depends(require_permission("fincas", "can_read"))])
def list_alerts(
    farm_id: uuid.UUID,
    days: int = Query(7, ge=1, le=90, description="Días hacia adelante para alertas próximas"),
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    _ = current_user
    return service.active_alerts(farm_id, days)


@router.get(
    "/preferences",
    response_model=NotificationPrefResponse,
    summary="Obtener preferencias de notificación del usuario",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def get_preferences(
    farm_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    """¿Qué? Devuelve las preferencias de notificación del usuario en la finca.

    COMO: miembro de la finca
    QUIERO: conocer mi canal y qué tipos de eventos tengo activados
    PARA:   que el formulario de la página de Alertas cargue mi configuración.
    """
    return service.get_or_create_prefs(current_user.id, farm_id)


@router.put(
    "/preferences",
    response_model=NotificationPrefResponse,
    summary="Actualizar preferencias de notificación",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def update_preferences(
    farm_id: uuid.UUID,
    payload: NotificationPrefUpdate,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    """¿Qué? Actualiza el canal y los tipos de evento notificados al usuario.

    ¿Para qué? Guardar lo que el usuario elige desde la página de Alertas.
    ¿Impacto? Valida canal/frecuencia; 422 si no son válidos.
    """
    # Canal o frecuencia inválidos -> InvalidRequestError -> 422 (app.core.error_handlers).
    return service.update_prefs(
        current_user.id,
        farm_id,
        channel=payload.channel,
        frequency=payload.frequency,
        notify_sanitary=payload.notify_sanitary,
        notify_low_stock=payload.notify_low_stock,
        notify_reproductive=payload.notify_reproductive,
        notify_birth=payload.notify_birth,
    )


@router.get(
    "/history",
    response_model=NotificationHistoryResponse,
    summary="Historial de notificaciones del usuario",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
async def get_history(
    farm_id: uuid.UUID,
    type: str | None = Query(None, description="Filtrar por tipo: sanitary, low_stock..."),
    unread_only: bool = Query(False, description="Solo no leídas"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    """¿Qué? Historial de notificaciones del usuario en la finca.

    ¿Para qué? Mostrar la página de Alertas y permitir filtrar por tipo.
    ¿Impacto? Solo lee: NO ejecuta el motor ni envía correos. Las notificaciones
              las genera la tarea programada (scheduler.py) cada
              NOTIFICATIONS_INTERVAL_MINUTES minutos.
    """

    items = service.list_notification_history(
        current_user.id,
        farm_id,
        notif_type=type,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    # Total real (antes era len(items): el tamaño de la página, no el total).
    total = service.count_notification_history(
        current_user.id, farm_id, notif_type=type, unread_only=unread_only
    )
    return NotificationHistoryResponse(
        items=[NotificationLogResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/history/unread-count",
    response_model=UnreadCountResponse,
    summary="Conteo de notificaciones sin leer",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def unread_count(
    farm_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    """¿Qué? Devuelve cuántas notificaciones del usuario están sin leer.

    ¿Para qué? Alimentar el badge de la campana del frontend. A diferencia del
               historial, NO ejecuta el motor de notificaciones, por lo que no
               genera envíos ni duplica ningún efecto colateral.
    ¿Impacto? Consulta de conteo ligera; no altera el historial ni preferencias.
    """
    unread = service.count_unread_notifications(current_user.id, farm_id)
    return UnreadCountResponse(farm_id=farm_id, unread_count=unread)


@router.put(
    "/history/{notification_id}/read",
    summary="Marcar una notificación como leída",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def mark_read(
    farm_id: uuid.UUID,
    notification_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    """¿Qué? Marca como leída la notificación indicada (si es del usuario).

    ¿Para qué? Que el usuario confirme/archive notificaciones en la web.
    ¿Impacto? 404 si no pertenece al usuario o no existe.
    """
    # Si no es del usuario en esta finca -> NotFoundError -> 404 (mismo mensaje de siempre).
    service.mark_as_read(current_user.id, farm_id, notification_id)
    return {"detail": "Notificación marcada como leída", "id": str(notification_id)}
