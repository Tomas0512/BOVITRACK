"""
Módulo: modules/milk_production/service.py
¿Qué? Reglas de negocio de la producción lechera: registrar, consultar,
      corregir y eliminar ordeños, y resumir la producción de un periodo.
¿Para qué? Llevar el historial de litros por bovino o por lote y detectar
           cuánto produce la finca por día, sesión y tipo de ordeño.
¿Impacto? Reglas que garantiza:
          - todo ordeño se asocia a un bovino o a un lote de ESTA finca;
          - no puede haber dos ordeños del mismo bovino en la misma fecha y sesión.
          No conoce HTTP ni SQLAlchemy; "¿este bovino o lote es de la finca?"
          lo pregunta a colaboradores inyectados (otros dominios).
"""

import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from app.modules.milk_production.models import MilkProduction
from app.modules.milk_production.repository import MilkProductionRepository
from app.modules.milk_production.schemas import MilkProductionCreate, MilkProductionUpdate
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder, BovineLookup, LandPlotLookup

RECORD_NOT_FOUND = "Registro de producción no encontrado"
NEEDS_BOVINE_OR_PLOT = "Debe indicar un bovino o un lote para el ordeño"
BOVINE_NOT_IN_FARM = "El bovino indicado no existe en esta finca"
PLOT_NOT_IN_FARM = "El lote indicado no existe en esta finca"
DUPLICATE_MILKING = "Ya existe un ordeño registrado para este bovino en esa fecha/sesión"


class MilkProductionService:
    """Casos de uso del módulo de producción lechera."""

    def __init__(
        self,
        repository: MilkProductionRepository,
        find_bovine: BovineLookup,
        land_plot_exists: LandPlotLookup,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._find_bovine = find_bovine
        self._land_plot_exists = land_plot_exists
        self._record_audit = record_audit

    # ── Validaciones ─────────────────────────────────────────

    def _ensure_bovine_in_farm(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> None:
        if self._find_bovine(farm_id, bovine_id) is None:
            raise BusinessRuleError(BOVINE_NOT_IN_FARM)

    def _ensure_plot_in_farm(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> None:
        if not self._land_plot_exists(farm_id, land_plot_id):
            raise BusinessRuleError(PLOT_NOT_IN_FARM)

    # ── Casos de uso ─────────────────────────────────────────

    def create_record(self, farm_id: uuid.UUID, data: MilkProductionCreate, user_id: uuid.UUID) -> MilkProduction:
        if data.bovine_id is None and data.land_plot_id is None:
            raise BusinessRuleError(NEEDS_BOVINE_OR_PLOT)
        if data.bovine_id:
            self._ensure_bovine_in_farm(farm_id, data.bovine_id)
        if data.land_plot_id:
            self._ensure_plot_in_farm(farm_id, data.land_plot_id)
        if data.bovine_id and self._repo.exists_for_bovine_session(
            data.bovine_id, data.milking_date, data.milking_session
        ):
            raise BusinessRuleError(DUPLICATE_MILKING)

        record = MilkProduction(farm_id=farm_id, registered_by=user_id, **data.model_dump())
        self._repo.add(record)
        self._repo.commit()
        self._repo.refresh(record)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="create",
            entity="milk_production",
            entity_id=str(record.id),
            details={"liters": str(record.quantity_liters)},
        )
        self._repo.commit()
        return record

    def list_records(
        self,
        farm_id: uuid.UUID,
        bovine_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        milking_session: str | None = None,
        milking_type: str | None = None,
    ) -> Sequence[MilkProduction]:
        """Ordeños de la finca, los más recientes primero."""
        return self._repo.list_by_farm(
            farm_id,
            bovine_id=bovine_id,
            date_from=date_from,
            date_to=date_to,
            milking_session=milking_session,
            milking_type=milking_type,
        )

    def get_record(self, farm_id: uuid.UUID, record_id: uuid.UUID) -> MilkProduction:
        record = self._repo.get_in_farm(farm_id, record_id)
        if record is None:
            raise NotFoundError(RECORD_NOT_FOUND)
        return record

    def update_record(
        self, farm_id: uuid.UUID, record_id: uuid.UUID, data: MilkProductionUpdate, user_id: uuid.UUID
    ) -> MilkProduction:
        record = self.get_record(farm_id, record_id)
        payload = data.model_dump(exclude_unset=True)

        if "bovine_id" in payload:
            if payload.get("bovine_id") is None and payload.get("land_plot_id") is None and record.land_plot_id is None:
                raise BusinessRuleError(NEEDS_BOVINE_OR_PLOT)
            if payload.get("bovine_id"):
                self._ensure_bovine_in_farm(farm_id, payload["bovine_id"])
        if payload.get("land_plot_id"):
            self._ensure_plot_in_farm(farm_id, payload["land_plot_id"])

        new_bovine = payload.get("bovine_id", record.bovine_id)
        new_date = payload.get("milking_date", record.milking_date)
        new_session = payload.get("milking_session", record.milking_session)
        if new_bovine and self._repo.exists_for_bovine_session(
            new_bovine, new_date, new_session, exclude_id=record_id
        ):
            raise BusinessRuleError(DUPLICATE_MILKING)

        for key, value in payload.items():
            setattr(record, key, value)
        self._repo.commit()
        self._repo.refresh(record)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="update",
            entity="milk_production",
            entity_id=str(record.id),
            details={"liters": str(record.quantity_liters)},
        )
        self._repo.commit()
        return record

    def delete_record(self, farm_id: uuid.UUID, record_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        record = self.get_record(farm_id, record_id)
        self._record_audit(
            user_id=str(user_id) if user_id else None,
            farm_id=str(farm_id),
            action="delete",
            entity="milk_production",
            entity_id=str(record.id),
        )
        self._repo.delete(record)
        self._repo.commit()

    def get_milk_summary(
        self, farm_id: uuid.UUID, date_from: date | None = None, date_to: date | None = None
    ) -> dict[str, Any]:
        """Total de litros, promedio diario, días con ordeño y top 10 de bovinos.

        Los montos se devuelven como texto para no perder precisión decimal en JSON.
        """
        rows = self._repo.list_by_farm(farm_id, date_from=date_from, date_to=date_to, newest_first=False)
        if not rows:
            return {
                "total_liters": "0",
                "avg_daily_liters": "0",
                "total_records": 0,
                "milking_days": 0,
                "by_session": {},
                "by_type": {},
                "top_bovines": [],
            }

        total = sum(r.quantity_liters for r in rows)
        days = {r.milking_date.date() for r in rows}
        by_session: dict[str, Decimal] = {}
        by_type: dict[str, Decimal] = {}
        per_bovine: dict[uuid.UUID, Decimal] = {}

        for r in rows:
            session = r.milking_session or "sin_sesión"
            by_session[session] = by_session.get(session, 0) + r.quantity_liters
            by_type[r.milking_type] = by_type.get(r.milking_type, 0) + r.quantity_liters
            if r.bovine_id:
                per_bovine[r.bovine_id] = per_bovine.get(r.bovine_id, 0) + r.quantity_liters

        top = sorted(per_bovine.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return {
            "total_liters": str(total),
            "avg_daily_liters": str((total / len(days)).quantize(Decimal("0.01"))) if days else "0",
            "total_records": len(rows),
            "milking_days": len(days),
            "by_session": {k: str(v) for k, v in by_session.items()},
            "by_type": {k: str(v) for k, v in by_type.items()},
            "top_bovines": [{"bovine_id": str(bid), "total_liters": str(amount)} for bid, amount in top],
        }
