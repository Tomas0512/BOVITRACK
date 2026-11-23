"""
Módulo: modules/livestock/service/weights.py
¿Qué? Casos de uso de los pesajes de un bovino (HU005): registrar, listar,
      consultar y eliminar.
¿Para qué? Seguir la evolución de peso de cada animal.
¿Impacto? Garantiza que:
          - solo se pesa un bovino ACTIVO de la finca (si no, 404);
          - la ganancia diaria se calcula contra el pesaje anterior
            ((peso nuevo - anterior) / días), o queda vacía si no hay anterior
            o es del mismo día;
          - el peso actual del bovino solo se actualiza si este pesaje es el
            más reciente (un pesaje atrasado no lo pisa).
"""

import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.modules.livestock.models import Bovine, Weight
from app.modules.livestock.repository import BovineRepository, WeightRepository
from app.modules.livestock.schemas import WeightCreate
from app.shared.exceptions import NotFoundError
from app.shared.ports import AuditRecorder

BOVINE_NOT_IN_FARM = "Bovino no encontrado en esta finca."
WEIGHT_NOT_FOUND = "Pesaje no encontrado."


def daily_gain(new_weight: Decimal, measured_at: date, previous: Weight | None) -> Decimal | None:
    """(peso nuevo - peso anterior) / días entre pesajes, redondeado a 2 decimales."""
    if previous is None:
        return None
    days = (measured_at - previous.measured_at).days
    if days <= 0:
        return None
    return round((new_weight - previous.weight_kg) / Decimal(days), 2)


class WeightService:
    """Casos de uso de los pesajes."""

    def __init__(self, weights: WeightRepository, bovines: BovineRepository, record_audit: AuditRecorder) -> None:
        self._weights = weights
        self._bovines = bovines
        self._record_audit = record_audit

    def _active_bovine(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine:
        bovine = self._bovines.get_active_in_farm(farm_id, bovine_id)
        if bovine is None:
            raise NotFoundError(BOVINE_NOT_IN_FARM)
        return bovine

    def create_weight(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, data: WeightCreate, user_id: uuid.UUID) -> Weight:
        bovine = self._active_bovine(farm_id, bovine_id)
        gain = daily_gain(data.weight_kg, data.measured_at, self._weights.previous_before(bovine_id, data.measured_at))
        record = Weight(farm_id=farm_id, bovine_id=bovine_id, registered_by=user_id, daily_gain=gain, **data.model_dump())
        self._weights.add(record)
        # Último pesaje ya guardado (el nuevo todavía no está en la BD): solo se
        # actualiza el peso actual si el nuevo es igual o más reciente.
        latest = self._weights.latest_measured_at(bovine_id)
        if latest is None or data.measured_at >= latest:
            bovine.current_weight = data.weight_kg
        self._weights.commit()
        self._weights.refresh(record)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="weight",
                           entity_id=str(record.id),
                           details={"bovine_id": str(bovine_id), "weight_kg": str(data.weight_kg)})
        self._weights.commit()
        return record

    def list_weights(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Sequence[Weight]:
        """Historial del bovino en orden cronológico."""
        self._active_bovine(farm_id, bovine_id)
        return self._weights.list_for_bovine(farm_id, bovine_id)

    def get_weight(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, weight_id: uuid.UUID) -> Weight:
        record = self._weights.get_in_farm(farm_id, bovine_id, weight_id)
        if record is None:
            raise NotFoundError(WEIGHT_NOT_FOUND)
        return record

    def delete_weight(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, weight_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Elimina el pesaje. Si era el más reciente, el peso actual pasa a ser el del
        pesaje anterior (antes quedaba el peso del pesaje borrado)."""
        record = self.get_weight(farm_id, bovine_id, weight_id)
        was_latest = record.measured_at == self._weights.latest_measured_at(bovine_id)
        self._weights.delete(record)
        if was_latest:
            self._weights.flush()  # la sesión no hace autoflush: sin esto el borrado no se vería
            previous = self._weights.latest(bovine_id)
            bovine = self._bovines.get_in_farm(farm_id, bovine_id)
            if previous is not None and bovine is not None:
                bovine.current_weight = previous.weight_kg
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="delete", entity="weight",
                           entity_id=str(weight_id), details={"bovine_id": str(bovine_id)})
        self._weights.commit()
