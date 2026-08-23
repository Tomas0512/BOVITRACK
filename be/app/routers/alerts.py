"""
Módulo: routers/alerts.py
¿Qué? Router para alertas sanitarias, de inventario y notificaciones (HU014).
¿Para qué? Endpoint unificado de alertas próximas/vencidas, preferencias de
           notificación por usuario y historial de notificaciones.
¿Impacto? Integración con frontend para mostrar AlertBanner, configurar las
          preferencias y consultar el historial.
"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.food import Food
from app.models.sanitary_plan import SanitaryPlan
from app.permissions import require_permission
from app.schemas.alert import (
    NotificationHistoryResponse,
    NotificationLogResponse,
    NotificationPrefResponse,
    NotificationPrefUpdate,
)
from app.services import notification_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/alerts", tags=["Alertas"])


@router.get("", summary="Obtener alertas activas de la finca")
def list_alerts(
    farm_id: uuid.UUID,
    days: int = Query(7, ge=1, le=90, description="Días hacia adelante para alertas próximas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    now = datetime.now()
    next_week = now + timedelta(days=days)

    overdue_stmt = select(SanitaryPlan).where(
        SanitaryPlan.farm_id == farm_id,
        SanitaryPlan.is_active.is_(True),
        SanitaryPlan.next_scheduled_date < now,
    )
    overdue = db.execute(overdue_stmt).scalars().all()

    upcoming_stmt = select(SanitaryPlan).where(
        SanitaryPlan.farm_id == farm_id,
        SanitaryPlan.is_active.is_(True),
        SanitaryPlan.next_scheduled_date >= now,
        SanitaryPlan.next_scheduled_date <= next_week,
    )
    upcoming = db.execute(upcoming_stmt).scalars().all()

    # Low stock food alerts (HU011.3)
    low_stmt = select(Food).where(
        Food.farm_id == farm_id,
        Food.is_active.is_(True),
        Food.min_stock_alert.isnot(None),
        Food.current_stock <= Food.min_stock_alert,
    ).order_by(Food.current_stock.asc())
    low_stock_foods = db.execute(low_stmt).scalars().all()

    return {
        "overdue": [
            {
                "id": str(p.id),
                "vaccine_or_treatment_name": p.vaccine_or_treatment_name,
                "treatment_type": p.treatment_type,
                "next_scheduled_date": p.next_scheduled_date.isoformat() if p.next_scheduled_date else None,
                "bovine_id": str(p.bovine_id) if p.bovine_id else None,
                "land_plot_id": str(p.land_plot_id) if p.land_plot_id else None,
            }
            for p in overdue
        ],
        "upcoming": [
            {
                "id": str(p.id),
                "vaccine_or_treatment_name": p.vaccine_or_treatment_name,
                "treatment_type": p.treatment_type,
                "next_scheduled_date": p.next_scheduled_date.isoformat() if p.next_scheduled_date else None,
                "bovine_id": str(p.bovine_id) if p.bovine_id else None,
                "land_plot_id": str(p.land_plot_id) if p.land_plot_id else None,
            }
            for p in upcoming
        ],
        "low_stock": [
            {
                "id": str(f.id),
                "name": f.name,
                "category": f.category,
                "current_stock": float(f.current_stock),
                "min_stock_alert": float(f.min_stock_alert) if f.min_stock_alert else None,
                "unit_of_measure": f.unit_of_measure,
            }
            for f in low_stock_foods
        ],
    }


@router.get(
    "/preferences",
    response_model=NotificationPrefResponse,
    summary="Obtener preferencias de notificación del usuario",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def get_preferences(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """¿Qué? Devuelve las preferencias de notificación del usuario en la finca.

    COMO: miembro de la finca
    QUIERO: conocer mi canal y qué tipos de eventos tengo activados
    PARA:   que el formulario de la página de Alertas cargue mi configuración.
    """
    return notification_service.get_or_create_prefs(db, current_user.id, farm_id)


@router.put(
    "/preferences",
    response_model=NotificationPrefResponse,
    summary="Actualizar preferencias de notificación",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def update_preferences(
    farm_id: uuid.UUID,
    payload: NotificationPrefUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """¿Qué? Actualiza el canal y los tipos de evento notificados al usuario.

    ¿Para qué? Guardar lo que el usuario elige desde la página de Alertas.
    ¿Impacto? Valida canal/frecuencia; 422 si no son válidos.
    """
    try:
        return notification_service.update_prefs(
            db,
            current_user.id,
            farm_id,
            channel=payload.channel,
            frequency=payload.frequency,
            notify_sanitary=payload.notify_sanitary,
            notify_low_stock=payload.notify_low_stock,
            notify_reproductive=payload.notify_reproductive,
            notify_birth=payload.notify_birth,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """¿Qué? Historial de notificaciones del usuario en la finca.

    ¿Para qué? Mostrar la página de Alertas y permitir filtrar por tipo.
    ¿Impacto? Ejecuta el motor de notificaciones on-demand (idempotente) para
              que el historial muestre los eventos pendientes sin duplicados.
    """
    await notification_service.run_notification_cycle(db, farm_id)

    items = notification_service.list_notification_history(
        db,
        current_user.id,
        farm_id,
        notif_type=type,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    total = len(items)
    return NotificationHistoryResponse(
        items=[NotificationLogResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.put(
    "/history/{notification_id}/read",
    summary="Marcar una notificación como leída",
    dependencies=[Depends(require_permission("fincas", "can_read"))],
)
def mark_read(
    farm_id: uuid.UUID,
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """¿Qué? Marca como leída la notificación indicada (si es del usuario).

    ¿Para qué? Que el usuario confirme/archive notificaciones en la web.
    ¿Impacto? 404 si no pertenece al usuario o no existe.
    """
    updated = notification_service.mark_as_read(
        db, current_user.id, farm_id, notification_id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada o no pertenece al usuario",
        )
    return {"detail": "Notificación marcada como leída", "id": str(notification_id)}
