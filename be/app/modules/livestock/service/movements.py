"""
Módulo: modules/livestock/service/movements.py
HU009 - Movimientos de animales
¿Qué? Casos de uso de las entradas y salidas del hato (compra, venta,
      traslado, nacimiento, muerte): registrar, listar, corregir y eliminar.
¿Para qué? Que el estado de cada bovino refleje su último movimiento: una
           venta lo marca como vendido, una muerte como muerto.
¿Impacto? Garantiza que el movimiento sea de un bovino de la finca (404), que
          no se repita el mismo tipo el mismo día para el mismo bovino (400) y
          que los movimientos son INMUTABLES: no se editan ni se eliminan (403).
          Un error se corrige registrando un movimiento nuevo.
"""

import uuid
from collections.abc import Sequence
from datetime import date

from app.modules.livestock.models import AnimalMovement
from app.modules.livestock.repository import BovineRepository, MovementRepository
from app.modules.livestock.schemas import MovementCreate
from app.shared.exceptions import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.shared.ports import AuditRecorder

BOVINE_NOT_IN_FARM = "Bovino no encontrado en esta finca"
MOVEMENT_NOT_FOUND = "Movimiento no encontrado"
DUPLICATE_MOVEMENT = "Ya existe un movimiento de este tipo para el bovino en esa fecha"
IMMUTABLE_UPDATE = "Los movimientos del hato son registros inmutables y no se pueden editar"
IMMUTABLE_DELETE = "Los movimientos del hato son registros inmutables y no se pueden eliminar"

# Tipo de movimiento -> estado que deja al bovino.
STATUS_BY_MOVEMENT = {
    "compra": "activo",
    "venta": "vendido",
    "traslado": "activo",
    "nacimiento": "activo",
    "muerte": "muerto",
}
# Movimientos que sacan al animal del hato (registran fecha y motivo de salida).
TERMINAL_MOVEMENTS = {"venta", "muerte"}



class MovementService:
    """Casos de uso de los movimientos de animales."""

    def __init__(self, movements: MovementRepository, bovines: BovineRepository, record_audit: AuditRecorder) -> None:
        self._movements = movements
        self._bovines = bovines
        self._record_audit = record_audit

    # ── Efecto del movimiento sobre el bovino ────────────────

    def _apply_to_bovine(self, farm_id: uuid.UUID, movement: AnimalMovement) -> None:
        if not movement.bovine_id or movement.movement_type not in STATUS_BY_MOVEMENT:
            return
        bovine = self._bovines.get_in_farm(farm_id, movement.bovine_id)
        if bovine is None:
            return
        new_status = STATUS_BY_MOVEMENT[movement.movement_type]
        bovine.status = new_status
        bovine.is_active = new_status == "activo"
        if movement.movement_type in TERMINAL_MOVEMENTS:
            bovine.exit_date = movement.movement_date
            bovine.exit_reason = movement.movement_type
        else:
            bovine.exit_date = None
            bovine.exit_reason = None

    # ── Casos de uso ─────────────────────────────────────────

    def create_movement(self, farm_id: uuid.UUID, data: MovementCreate, user_id: uuid.UUID) -> AnimalMovement:
        if data.bovine_id:
            if self._bovines.get_in_farm(farm_id, data.bovine_id) is None:
                raise NotFoundError(BOVINE_NOT_IN_FARM)
            if self._movements.duplicate_exists(data.bovine_id, data.movement_type, data.movement_date):
                raise BusinessRuleError(DUPLICATE_MOVEMENT)

        movement = AnimalMovement(farm_id=farm_id, registered_by=user_id, **data.model_dump())
        self._movements.add(movement)
        if data.bovine_id:
            self._apply_to_bovine(farm_id, movement)
        self._movements.commit()
        self._movements.refresh(movement)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="movement",
                           entity_id=str(movement.id),
                           details={"type": data.movement_type,
                                    "bovine_id": str(data.bovine_id) if data.bovine_id else None})
        self._movements.commit()
        return movement

    def list_movements(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        movement_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Sequence[AnimalMovement]:
        return self._movements.list_by_farm(
            farm_id, bovine_id=bovine_id, movement_type=movement_type, date_from=date_from, date_to=date_to
        )

    def get_movement(self, farm_id: uuid.UUID, movement_id: uuid.UUID) -> AnimalMovement:
        movement = self._movements.get_in_farm(farm_id, movement_id)
        if movement is None:
            raise NotFoundError(MOVEMENT_NOT_FOUND)
        return movement

    def update_movement(self, farm_id: uuid.UUID, movement_id: uuid.UUID) -> None:
        """Regla: los movimientos son inmutables. Un error se corrige con un movimiento nuevo."""
        raise PermissionDeniedError(IMMUTABLE_UPDATE)

    def delete_movement(self, farm_id: uuid.UUID, movement_id: uuid.UUID) -> None:
        """Regla: los movimientos son inmutables (son la historia del hato)."""
        raise PermissionDeniedError(IMMUTABLE_DELETE)
