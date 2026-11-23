"""
Módulo: modules/health/service.py
¿Qué? Reglas de negocio de la sanidad del hato, en dos agregados:
      - TreatmentService: tratamientos ya aplicados (vacunas, desparasitaciones,
        tratamientos veterinarios) a un bovino o a un lote.
      - SanitaryPlanService: protocolos programados (p. ej. aftosa cada 180 días)
        con su próxima fecha de aplicación.
¿Para qué? Registrar qué se aplicó y planificar qué falta aplicar, para que
           ninguna vacuna se pase de fecha.
¿Impacto? Garantiza que bovino, lote y alimento referenciados sean de ESTA finca,
          y que al marcar un plan como aplicado la próxima fecha se recalcule
          (hoy + frecuencia). No conoce HTTP ni SQLAlchemy: lo de otros dominios
          llega por puertos.
"""

import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta
from typing import Protocol

from app.modules.health.models import SanitaryPlan, Treatment
from app.modules.health.repository import SanitaryPlanRepository, TreatmentRepository
from app.modules.health.schemas import SanitaryPlanCreate, SanitaryPlanUpdate, TreatmentCreate
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder, BovineLookup, FarmScopeChecker, LandPlotLookup

TREATMENT_NOT_FOUND = "Tratamiento no encontrado"
PLAN_NOT_FOUND = "Plan sanitario no encontrado"
BOVINE_NOT_IN_FARM = "El bovino indicado no existe en esta finca"
PLOT_NOT_IN_FARM = "El lote indicado no existe en esta finca"
FOOD_NOT_IN_FARM = "El alimento indicado no existe en esta finca"


class FoodLookup(Protocol):
    """Puerto hacia inventario: ¿el alimento existe y es de la finca?

    Propio de este módulo (solo salud lo necesita). Lo implementa
    inventory.build_food_lookup.
    """

    def __call__(self, farm_id: uuid.UUID, food_id: uuid.UUID) -> bool: ...


def _user(user_id: uuid.UUID | None) -> str | None:
    return str(user_id) if user_id else None


class TreatmentService:
    """Casos de uso de los tratamientos aplicados."""

    def __init__(
        self,
        repository: TreatmentRepository,
        find_bovine: BovineLookup,
        land_plot_exists: LandPlotLookup,
        food_exists: FoodLookup,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._find_bovine = find_bovine
        self._land_plot_exists = land_plot_exists
        self._food_exists = food_exists
        self._record_audit = record_audit

    def create_treatment(self, farm_id: uuid.UUID, data: TreatmentCreate, user_id: uuid.UUID) -> Treatment:
        if data.bovine_id and self._find_bovine(farm_id, data.bovine_id) is None:
            raise BusinessRuleError(BOVINE_NOT_IN_FARM)
        if data.land_plot_id and not self._land_plot_exists(farm_id, data.land_plot_id):
            raise BusinessRuleError(PLOT_NOT_IN_FARM)
        if data.food_id and not self._food_exists(farm_id, data.food_id):
            raise BusinessRuleError(FOOD_NOT_IN_FARM)

        treatment = Treatment(farm_id=farm_id, applied_by=user_id, **data.model_dump())
        self._repo.add(treatment)
        self._repo.commit()
        self._repo.refresh(treatment)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="treatment",
                           entity_id=str(treatment.id), details={"type": treatment.treatment_type})
        self._repo.commit()
        return treatment

    def list_treatments(self, farm_id: uuid.UUID, bovine_id: uuid.UUID | None = None) -> Sequence[Treatment]:
        return self._repo.list_by_farm(farm_id, bovine_id=bovine_id)

    def get_treatment(self, farm_id: uuid.UUID, treatment_id: uuid.UUID) -> Treatment:
        treatment = self._repo.get_in_farm(farm_id, treatment_id)
        if treatment is None:
            raise NotFoundError(TREATMENT_NOT_FOUND)
        return treatment

    def delete_treatment(self, farm_id: uuid.UUID, treatment_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Borrado físico (un tratamiento no tiene registros que dependan de él)."""
        treatment = self.get_treatment(farm_id, treatment_id)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="delete", entity="treatment",
                           entity_id=str(treatment.id), details={"type": treatment.treatment_type})
        self._repo.delete(treatment)
        self._repo.commit()


class SanitaryPlanService:
    """Casos de uso de los planes sanitarios programados."""

    def __init__(
        self,
        repository: SanitaryPlanRepository,
        ensure_farm_scope: FarmScopeChecker,
        record_audit: AuditRecorder,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repo = repository
        self._ensure_farm_scope = ensure_farm_scope
        self._record_audit = record_audit
        self._now = now

    def create_sanitary_plan(
        self, farm_id: uuid.UUID, data: SanitaryPlanCreate, user_id: uuid.UUID | None = None
    ) -> SanitaryPlan:
        self._ensure_farm_scope(farm_id, bovine_id=data.bovine_id, land_plot_id=data.land_plot_id)
        plan = SanitaryPlan(farm_id=farm_id, created_by=user_id or uuid.uuid4(), **data.model_dump())
        self._repo.add(plan)
        self._repo.commit()
        self._repo.refresh(plan)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="create", entity="sanitary_plan",
                           entity_id=str(plan.id), details={"name": plan.vaccine_or_treatment_name})
        self._repo.commit()
        return plan

    def list_sanitary_plans(
        self,
        farm_id: uuid.UUID,
        bovine_id: uuid.UUID | None = None,
        land_plot_id: uuid.UUID | None = None,
        include_inactive: bool = False,
    ) -> Sequence[SanitaryPlan]:
        return self._repo.list_by_farm(
            farm_id, bovine_id=bovine_id, land_plot_id=land_plot_id, include_inactive=include_inactive
        )

    def get_sanitary_plan(self, farm_id: uuid.UUID, plan_id: uuid.UUID) -> SanitaryPlan:
        plan = self._repo.get_in_farm(farm_id, plan_id)
        if plan is None:
            raise NotFoundError(PLAN_NOT_FOUND)
        return plan

    def update_sanitary_plan(
        self, farm_id: uuid.UUID, plan_id: uuid.UUID, data: SanitaryPlanUpdate, user_id: uuid.UUID | None = None
    ) -> SanitaryPlan:
        plan = self.get_sanitary_plan(farm_id, plan_id)
        changes = data.model_dump(exclude_unset=True)
        # Se revalida el alcance con los valores finales (nuevos o los que ya tenía).
        self._ensure_farm_scope(
            farm_id,
            bovine_id=changes.get("bovine_id", plan.bovine_id),
            land_plot_id=changes.get("land_plot_id", plan.land_plot_id),
        )
        for field, value in changes.items():
            setattr(plan, field, value)
        self._repo.commit()
        self._repo.refresh(plan)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="update", entity="sanitary_plan",
                           entity_id=str(plan.id), details={"name": plan.vaccine_or_treatment_name})
        self._repo.commit()
        return plan

    def mark_as_applied(self, farm_id: uuid.UUID, plan_id: uuid.UUID, user_id: uuid.UUID | None = None) -> SanitaryPlan:
        """Registra la aplicación de hoy y programa la próxima: hoy + frequency_days."""
        plan = self.get_sanitary_plan(farm_id, plan_id)
        now = self._now()
        plan.last_applied_date = now
        plan.next_scheduled_date = now + timedelta(days=plan.frequency_days)
        self._repo.commit()
        self._repo.refresh(plan)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="update", entity="sanitary_plan",
                           entity_id=str(plan.id),
                           details={"action": "marked_as_applied", "name": plan.vaccine_or_treatment_name})
        self._repo.commit()
        return plan

    def deactivate_sanitary_plan(self, farm_id: uuid.UUID, plan_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Borrado lógico: el plan deja de generar alertas pero se conserva."""
        plan = self.get_sanitary_plan(farm_id, plan_id)
        plan.is_active = False
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="delete", entity="sanitary_plan",
                           entity_id=str(plan.id), details={"name": plan.vaccine_or_treatment_name})
        self._repo.commit()
