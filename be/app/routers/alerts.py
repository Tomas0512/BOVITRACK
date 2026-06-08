"""
Módulo: routers/alerts.py
¿Qué? Router para alertas sanitarias y de inventario.
¿Para qué? Endpoint unificado de alertas próximas/vencidas.
¿Impacto? Integración con frontend para mostrar AlertBanner.
"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.sanitary_plan import SanitaryPlan

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
    }
