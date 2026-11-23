"""
Módulo: modules/reproduction/service.py
¿Qué? Reglas de negocio del control reproductivo: registrar, consultar,
      corregir y eliminar eventos (celo, servicio, diagnóstico, parto...).
¿Para qué? Seguir el ciclo de cada hembra y registrar automáticamente las
           crías que nacen en un parto.
¿Impacto? Reglas que garantiza:
          - madre, toro y cría deben ser bovinos de ESTA finca;
          - solo una hembra puede registrar un parto;
          - un servicio sin fecha probable de parto la recibe: fecha + 283 días;
          - un parto con resultado macho/hembra/gemelos crea las crías en ganado.
          No conoce HTTP ni SQLAlchemy. Crear un bovino es responsabilidad del
          dominio de ganado: este servicio lo pide a un CalfRegistrar inyectado.
"""

import uuid
from collections.abc import Sequence
from datetime import date, timedelta
from typing import Protocol

from app.modules.reproduction.models import ReproductiveEvent
from app.modules.reproduction.repository import ReproductiveEventRepository
from app.modules.reproduction.schemas import ReproductiveEventCreate, ReproductiveEventUpdate
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder, BovineLookup, FarmScopeChecker

GESTATION_DAYS = 283

# Resultado del parto -> sexo de cada cría que se registra.
CALF_SEXES_BY_RESULT: dict[str, list[str]] = {
    "macho": ["macho"],
    "hembra": ["hembra"],
    "gemelos": ["macho", "hembra"],
}

EVENT_NOT_FOUND = "Evento reproductivo no encontrado"
MOTHER_NOT_IN_FARM = "El bovino indicado no existe en esta finca"
ONLY_FEMALES_GIVE_BIRTH = "Solo una hembra puede registrar un parto"
BULL_NOT_IN_FARM = "El toro indicado no existe en esta finca"
CALF_NOT_IN_FARM = "La cría indicada no existe en esta finca"


class CalfRegistrar(Protocol):
    """Puerto hacia ganado: registra una cría nacida en la finca y devuelve su id.

    Es propio de este módulo (solo reproducción lo necesita), por eso se define
    aquí y no en app.shared.ports.
    """

    def __call__(
        self,
        farm_id: uuid.UUID,
        *,
        identification_number: str,
        sex: str,
        birth_date: date,
        mother_id: uuid.UUID,
        registered_by: uuid.UUID,
    ) -> uuid.UUID: ...


def calf_identification(mother_id: uuid.UUID, birth_date: date, index: int) -> str:
    """Identificación provisional de la cría: CRIA-<6 primeros de la madre>-<AAAAMMDD>-<n>."""
    return f"CRIA-{str(mother_id)[:6]}-{birth_date.strftime('%Y%m%d')}-{index}"


class ReproductionService:
    """Casos de uso del módulo de reproducción."""

    def __init__(
        self,
        repository: ReproductiveEventRepository,
        find_bovine: BovineLookup,
        ensure_farm_scope: FarmScopeChecker,
        register_calf: CalfRegistrar,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._find_bovine = find_bovine
        self._ensure_farm_scope = ensure_farm_scope
        self._register_calf = register_calf
        self._record_audit = record_audit

    def create_event(self, farm_id: uuid.UUID, data: ReproductiveEventCreate, user_id: uuid.UUID) -> ReproductiveEvent:
        if data.bovine_id:
            mother = self._find_bovine(farm_id, data.bovine_id)
            if mother is None:
                raise BusinessRuleError(MOTHER_NOT_IN_FARM)
            if data.event_type == "parto" and mother.sex != "hembra":
                raise BusinessRuleError(ONLY_FEMALES_GIVE_BIRTH)
        if data.bull_id and self._find_bovine(farm_id, data.bull_id) is None:
            raise BusinessRuleError(BULL_NOT_IN_FARM)
        if data.calf_id and self._find_bovine(farm_id, data.calf_id) is None:
            raise BusinessRuleError(CALF_NOT_IN_FARM)

        event = ReproductiveEvent(farm_id=farm_id, registered_by=user_id, **data.model_dump())
        self._apply_due_date(event)
        if event.event_type == "parto":
            self._register_calves(farm_id, event, user_id)

        self._repo.add(event)
        self._repo.commit()
        self._repo.refresh(event)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="create",
            entity="reproductive_event",
            entity_id=str(event.id),
            details={"type": event.event_type},
        )
        self._repo.commit()
        return event

    def list_events(
        self,
        farm_id: uuid.UUID,
        bovine_id: uuid.UUID | None = None,
        event_type: str | None = None,
    ) -> Sequence[ReproductiveEvent]:
        return self._repo.list_by_farm(farm_id, bovine_id=bovine_id, event_type=event_type)

    def get_event(self, farm_id: uuid.UUID, event_id: uuid.UUID) -> ReproductiveEvent:
        event = self._repo.get_in_farm(farm_id, event_id)
        if event is None:
            raise NotFoundError(EVENT_NOT_FOUND)
        return event

    def update_event(
        self, farm_id: uuid.UUID, event_id: uuid.UUID, data: ReproductiveEventUpdate, user_id: uuid.UUID
    ) -> ReproductiveEvent:
        event = self.get_event(farm_id, event_id)
        changes = data.model_dump(exclude_unset=True)
        # Evita IDOR: toro y cría nuevos deben ser de esta finca.
        if changes.get("bull_id") is not None:
            self._ensure_farm_scope(farm_id, bovine_id=changes["bull_id"])
        if changes.get("calf_id") is not None:
            self._ensure_farm_scope(farm_id, bovine_id=changes["calf_id"])
        for field, value in changes.items():
            setattr(event, field, value)

        self._apply_due_date(event)
        if event.event_type == "parto" and not event.calf_id:
            self._register_calves(farm_id, event, user_id)

        self._repo.commit()
        self._repo.refresh(event)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="update",
            entity="reproductive_event",
            entity_id=str(event.id),
            details={"type": event.event_type},
        )
        self._repo.commit()
        return event

    def delete_event(self, farm_id: uuid.UUID, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        event = self.get_event(farm_id, event_id)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="delete",
            entity="reproductive_event",
            entity_id=str(event.id),
        )
        self._repo.delete(event)
        self._repo.commit()

    # ── Reglas internas ──────────────────────────────────────

    @staticmethod
    def _apply_due_date(event: ReproductiveEvent) -> None:
        """Un servicio sin fecha probable de parto la recibe: fecha + 283 días."""
        if event.event_type == "servicio" and event.due_date is None:
            event.due_date = event.event_date + timedelta(days=GESTATION_DAYS)

    def _register_calves(self, farm_id: uuid.UUID, event: ReproductiveEvent, user_id: uuid.UUID) -> None:
        """Registra en ganado una cría por cada sexo del resultado; enlaza la primera."""
        sexes = CALF_SEXES_BY_RESULT.get(event.result or "")
        if not sexes:
            return
        calf_ids = [
            self._register_calf(
                farm_id,
                identification_number=calf_identification(event.bovine_id, event.event_date, i + 1),
                sex=sex,
                birth_date=event.event_date,
                mother_id=event.bovine_id,
                registered_by=user_id,
            )
            for i, sex in enumerate(sexes)
        ]
        event.calf_id = calf_ids[0]
