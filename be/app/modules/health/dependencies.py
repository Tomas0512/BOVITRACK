"""
Módulo: modules/health/dependencies.py (composición del módulo)
¿Qué? 1. Arma los servicios de tratamientos y planes sanitarios por request.
      2. Ofrece a otros módulos el puerto SanitaryAlertsSource (planes vencidos
         y próximos), que usa notifications.
¿Para qué? Que "qué es un plan vencido" se defina una sola vez, en el módulo
           dueño de los planes.
¿Impacto? Es el único archivo de health que conoce otros módulos: usa la API
          pública de inventory (¿el alimento es de la finca?). Health está por
          debajo de notifications y por encima de inventory en las capas de
          módulos, así que nunca puede formarse un ciclo.
"""

import uuid
from datetime import datetime
from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms, inventory, livestock
from app.modules.health.models import SanitaryPlan
from app.modules.health.repository import SanitaryPlanRepository, TreatmentRepository
from app.modules.health.service import SanitaryPlanService, TreatmentService
from app.shared.ports import SanitaryAlertsSource, SanitaryDue

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_treatment_service(db: Session = Depends(get_db)) -> TreatmentService:
    """Dependencia de FastAPI: un TreatmentService por request."""
    return TreatmentService(
        repository=TreatmentRepository(db),
        find_bovine=livestock.build_bovine_lookup(db),
        land_plot_exists=farms.build_land_plot_lookup(db),
        food_exists=inventory.build_food_lookup(db),
        record_audit=partial(add_audit_log, db),
    )


def get_sanitary_plan_service(db: Session = Depends(get_db)) -> SanitaryPlanService:
    """Dependencia de FastAPI: un SanitaryPlanService por request."""
    return SanitaryPlanService(
        repository=SanitaryPlanRepository(db),
        ensure_farm_scope=farms.build_farm_scope_checker(db, find_bovine=livestock.build_bovine_lookup(db)),
        record_audit=partial(add_audit_log, db),
    )


# ── Puerto que salud ofrece a otros módulos ───────────────────────


def _to_sanitary_due(plan: SanitaryPlan) -> SanitaryDue:
    return SanitaryDue(
        id=plan.id,
        vaccine_or_treatment_name=plan.vaccine_or_treatment_name,
        treatment_type=plan.treatment_type,
        next_scheduled_date=plan.next_scheduled_date,
        bovine_id=plan.bovine_id,
        land_plot_id=plan.land_plot_id,
    )


class _SanitaryAlerts:
    """SanitaryAlertsSource sobre el repositorio de planes (solo planes activos)."""

    def __init__(self, db: Session) -> None:
        self._repo = SanitaryPlanRepository(db)

    def overdue(self, farm_id: uuid.UUID, now: datetime) -> list[SanitaryDue]:
        return [_to_sanitary_due(p) for p in self._repo.overdue(farm_id, now)]

    def upcoming(self, farm_id: uuid.UUID, now: datetime, until: datetime) -> list[SanitaryDue]:
        return [_to_sanitary_due(p) for p in self._repo.upcoming(farm_id, now, until)]


def build_sanitary_alerts(db: Session) -> SanitaryAlertsSource:
    """SanitaryAlertsSource: planes vencidos y próximos de una finca."""
    return _SanitaryAlerts(db)
