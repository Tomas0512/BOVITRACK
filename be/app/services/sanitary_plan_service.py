"""
Módulo: services/sanitary_plan_service.py
¿Qué? Capa de servicio para planes sanitarios (vacunas, tratamientos).
¿Para qué? Gestionar qué vacunas debe recibir cada bovino o lote y cuándo.
¿Impacto? Coordina alertas sanitarias y calendarios de aplicación.
"""

import uuid
from datetime import datetime, timedelta
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sanitary_plan import SanitaryPlan
from app.schemas.sanitary_plan import (
    SanitaryPlanCreate,
    SanitaryPlanUpdate,
)
from app.services.audit_service import add_audit_log


def create_sanitary_plan(
    db: Session,
    farm_id: uuid.UUID,
    data: SanitaryPlanCreate,
    user_id: uuid.UUID | None = None,
) -> SanitaryPlan:
    """¿Qué? Registra un nuevo plan sanitario para un bovino o lote.
    ¿Para qué? Programar vacunas y tratamientos periódicos.
    ¿Impacto? El plan queda activo y genera alertas según frecuencia.
    """
    plan = SanitaryPlan(
        farm_id=farm_id,
        created_by=user_id or uuid.uuid4(),
        **data.model_dump()
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    add_audit_log(
        db,
        user_id=str(user_id) if user_id else None,
        farm_id=str(farm_id),
        action="create",
        entity="sanitary_plan",
        entity_id=str(plan.id),
        details={"name": plan.vaccine_or_treatment_name},
    )
    db.commit()
    return plan


def list_sanitary_plans(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = None,
    land_plot_id: uuid.UUID | None = None,
    include_inactive: bool = False,
) -> Sequence[SanitaryPlan]:
    """¿Qué? Lista planes sanitarios de una finca, opcionalmente filtrados.
    ¿Para qué? Mostrar el calendario sanitario del hato.
    ¿Impacto? Por defecto excluye planes inactivos (is_active=False).
    """
    stmt = select(SanitaryPlan).where(SanitaryPlan.farm_id == farm_id)

    if not include_inactive:
        stmt = stmt.where(SanitaryPlan.is_active.is_(True))

    if bovine_id:
        stmt = stmt.where(SanitaryPlan.bovine_id == bovine_id)

    if land_plot_id:
        stmt = stmt.where(SanitaryPlan.land_plot_id == land_plot_id)

    return db.execute(stmt.order_by(SanitaryPlan.next_scheduled_date.asc())).scalars().all()


def get_sanitary_plan(
    db: Session,
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
) -> SanitaryPlan:
    """¿Qué? Obtiene un plan sanitario por ID dentro de una finca.
    ¿Para qué? Consultar detalle o validar existencia antes de operar.
    ¿Impacto? Filtra por farm_id para evitar acceso cruzado entre fincas.
    """
    stmt = select(SanitaryPlan).where(
        SanitaryPlan.id == plan_id,
        SanitaryPlan.farm_id == farm_id,
    )
    plan = db.execute(stmt).scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan sanitario no encontrado",
        )
    return plan


def update_sanitary_plan(
    db: Session,
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    data: SanitaryPlanUpdate,
    user_id: uuid.UUID | None = None,
) -> SanitaryPlan:
    """¿Qué? Actualiza los campos enviados de un plan sanitario.
    ¿Para qué? Modificar fechas, observaciones, estado sin reenviar todo.
    ¿Impacto? exclude_unset=True asegura actualización parcial segura.
    """
    plan = get_sanitary_plan(db, farm_id, plan_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    add_audit_log(
        db,
        user_id=str(user_id) if user_id else None,
        farm_id=str(farm_id),
        action="update",
        entity="sanitary_plan",
        entity_id=str(plan.id),
        details={"name": plan.vaccine_or_treatment_name},
    )
    db.commit()
    return plan


def mark_as_applied(
    db: Session,
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
) -> SanitaryPlan:
    """¿Qué? Marca un plan como aplicado y recalcula la próxima fecha.
    ¿Para qué? Registrar que la vacuna/tratamiento se aplicó hoy.
    ¿Impacto? Actualiza last_applied_date y recalcula next_scheduled_date
              sumando frequency_days a hoy.
    """
    plan = get_sanitary_plan(db, farm_id, plan_id)
    now = datetime.now()
    plan.last_applied_date = now
    plan.next_scheduled_date = now + timedelta(days=plan.frequency_days)
    db.commit()
    db.refresh(plan)
    add_audit_log(
        db,
        user_id=str(user_id) if user_id else None,
        farm_id=str(farm_id),
        action="update",
        entity="sanitary_plan",
        entity_id=str(plan.id),
        details={"action": "marked_as_applied", "name": plan.vaccine_or_treatment_name},
    )
    db.commit()
    return plan


def deactivate_sanitary_plan(
    db: Session,
    farm_id: uuid.UUID,
    plan_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
) -> None:
    """¿Qué? Desactiva un plan sanitario (soft delete).
    ¿Para qué? Discontinuar un tratamiento sin perder el historial.
    ¿Impacto? El plan deja de generar alertas pero se conserva para auditoría.
    """
    plan = get_sanitary_plan(db, farm_id, plan_id)
    plan.is_active = False
    add_audit_log(
        db,
        user_id=str(user_id) if user_id else None,
        farm_id=str(farm_id),
        action="delete",
        entity="sanitary_plan",
        entity_id=str(plan.id),
        details={"name": plan.vaccine_or_treatment_name},
    )
    db.commit()


def get_overdue_plans(
    db: Session,
    farm_id: uuid.UUID,
) -> Sequence[SanitaryPlan]:
    """¿Qué? Lista planes sanitarios que ya deberían haberse aplicado.
    ¿Para qué? Alertar sobre vacunas/tratamientos atrasados.
    ¿Impacto? Filtra planes donde next_scheduled_date < hoy.
    """
    now = datetime.now()
    stmt = select(SanitaryPlan).where(
        SanitaryPlan.farm_id == farm_id,
        SanitaryPlan.is_active.is_(True),
        SanitaryPlan.next_scheduled_date < now,
    )
    return db.execute(stmt).scalars().all()
