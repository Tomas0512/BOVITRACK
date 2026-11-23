"""
Módulo: modules/inventory/service.py
¿Qué? Reglas de negocio del inventario de alimentos e insumos: registrar y
      editar insumos, registrar consumos (descuentan stock), compras (suman
      stock y fijan el costo) y ajustes manuales, con trazabilidad de cada
      movimiento.
¿Para qué? Saber cuánto hay de cada insumo, en qué se gastó y cuánto costó.
¿Impacto? Garantiza que:
          - el stock nunca queda negativo (consumo mayor al disponible -> 400,
            ajuste que bajaría de 0 -> 400);
          - todo cambio de stock deja un StockMovement con el antes y el después;
          - un consumo solo apunta a bovino, lote o potrero de ESTA finca, y el
            potrero debe ser coherente con el lote.
          No conoce HTTP ni SQLAlchemy; bovinos, lotes y potreros los valida
          con colaboradores inyectados.
"""

import uuid
from collections.abc import Sequence
from typing import Any
from datetime import date, datetime, timezone
from decimal import Decimal

from app.modules.inventory.models import Consumption, Food, StockMovement
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import ConsumptionCreate, FoodCreate, FoodUpdate
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder, BovineLookup, FarmScopeChecker, PaddockLookup

FOOD_NOT_FOUND = "Alimento no encontrado"
PADDOCK_NOT_IN_FARM = "El potrero indicado no existe en esta finca."
PADDOCK_OTHER_PLOT = "El potrero indicado pertenece a otro lote."
CALF_NOT_FOUND = "Ternero no encontrado"
QUANTITY_NOT_POSITIVE = "La cantidad debe ser mayor a 0"


def _user(user_id: uuid.UUID | None) -> str | None:
    return str(user_id) if user_id else None


class InventoryService:
    """Casos de uso del módulo de inventario."""

    def __init__(
        self,
        repository: InventoryRepository,
        ensure_farm_scope: FarmScopeChecker,
        find_paddock: PaddockLookup,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._ensure_farm_scope = ensure_farm_scope
        self._find_paddock = find_paddock
        self._record_audit = record_audit

    # ── Alimentos ────────────────────────────────────────────

    def create_food(self, farm_id: uuid.UUID, data: FoodCreate, user_id: uuid.UUID | None = None) -> Food:
        food = Food(farm_id=farm_id, **data.model_dump())
        self._repo.add(food)
        self._repo.commit()
        self._repo.refresh(food)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="create", entity="food",
                           entity_id=str(food.id), details={"name": food.name})
        self._repo.commit()
        return food

    def list_foods(self, farm_id: uuid.UUID) -> Sequence[Food]:
        return self._repo.list_active_foods(farm_id)

    def get_food(self, farm_id: uuid.UUID, food_id: uuid.UUID) -> Food:
        food = self._repo.get_food_in_farm(farm_id, food_id)
        if food is None:
            raise NotFoundError(FOOD_NOT_FOUND)
        return food

    def update_food(
        self, farm_id: uuid.UUID, food_id: uuid.UUID, data: FoodUpdate, user_id: uuid.UUID | None = None
    ) -> Food:
        food = self.get_food(farm_id, food_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(food, field, value)
        self._repo.commit()
        self._repo.refresh(food)
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="update", entity="food",
                           entity_id=str(food.id), details={"name": food.name})
        self._repo.commit()
        return food

    def delete_food(self, farm_id: uuid.UUID, food_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Borrado lógico: el insumo se oculta, sus consumos y movimientos se conservan."""
        food = self.get_food(farm_id, food_id)
        food.is_active = False
        self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="delete", entity="food",
                           entity_id=str(food.id), details={"name": food.name})
        self._repo.commit()

    def get_low_stock_foods(self, farm_id: uuid.UUID) -> Sequence[Food]:
        """Insumos en o por debajo de su mínimo, del más crítico al menos crítico."""
        return self._repo.low_stock_by_ratio(farm_id)

    # ── Consumos ─────────────────────────────────────────────

    def create_consumption(self, farm_id: uuid.UUID, data: ConsumptionCreate, user_id: uuid.UUID) -> Consumption:
        """Registra un consumo y descuenta el stock. Nunca deja el stock negativo."""
        food = self.get_food(farm_id, data.food_id)
        self._ensure_farm_scope(farm_id, bovine_id=data.bovine_id, land_plot_id=data.land_plot_id)

        if data.paddock_id:
            paddock = self._find_paddock(farm_id, data.paddock_id)
            if paddock is None:
                raise BusinessRuleError(PADDOCK_NOT_IN_FARM)
            if data.land_plot_id is not None and paddock.land_plot_id != data.land_plot_id:
                raise BusinessRuleError(PADDOCK_OTHER_PLOT)
            if data.land_plot_id is None:
                data.land_plot_id = paddock.land_plot_id

        if food.current_stock < data.quantity:
            raise BusinessRuleError(f"Stock insuficiente. Disponible: {food.current_stock} {food.unit_of_measure}")

        stock_before = food.current_stock
        food.current_stock -= data.quantity
        self._record_stock_movement(
            farm_id=farm_id,
            food_id=food.id,
            movement_type="consumption",
            quantity=-data.quantity,
            stock_before=stock_before,
            stock_after=food.current_stock,
            registered_by=user_id,
            reference_type="consumption",
            notes=f"Consumo: {data.observations or ''}".strip() or None,
            movement_date=data.feeding_date,
        )
        consumption = Consumption(farm_id=farm_id, registered_by=user_id, **data.model_dump())
        self._repo.add(consumption)
        self._repo.commit()
        self._repo.refresh(consumption)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="consumption",
                           entity_id=str(consumption.id),
                           details={"food_id": str(data.food_id), "quantity": str(data.quantity)})
        self._repo.commit()
        return consumption

    def list_consumptions(
        self, farm_id: uuid.UUID, food_id: uuid.UUID | None = None, bovine_id: uuid.UUID | None = None
    ) -> Sequence[Consumption]:
        return self._repo.list_consumptions(farm_id, food_id=food_id, bovine_id=bovine_id)

    # ── Movimientos de stock (HU011) ─────────────────────────

    def _record_stock_movement(
        self,
        *,
        farm_id: uuid.UUID,
        food_id: uuid.UUID,
        movement_type: str,
        quantity: Decimal,
        stock_before: Decimal,
        stock_after: Decimal,
        registered_by: uuid.UUID,
        unit_cost: Decimal | None = None,
        total_cost: Decimal | None = None,
        reference_type: str | None = None,
        reference_id: uuid.UUID | None = None,
        notes: str | None = None,
        movement_date: datetime | None = None,
    ) -> StockMovement:
        """Deja constancia de un cambio de stock con el antes y el después."""
        movement = StockMovement(
            farm_id=farm_id,
            food_id=food_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            stock_before=stock_before,
            stock_after=stock_after,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            registered_by=registered_by,
            movement_date=movement_date or datetime.now(timezone.utc),
        )
        self._repo.add(movement)
        self._repo.flush()
        return movement

    def record_purchase(
        self,
        farm_id: uuid.UUID,
        food_id: uuid.UUID,
        quantity: Decimal,
        unit_cost: Decimal,
        user_id: uuid.UUID,
        movement_date: datetime | None = None,
        notes: str | None = None,
    ) -> tuple[Food, StockMovement]:
        """Compra: suma stock, actualiza el costo unitario y registra el costo total."""
        food = self.get_food(farm_id, food_id)
        stock_before = food.current_stock
        total_cost = quantity * unit_cost
        food.current_stock += quantity
        food.cost_per_unit = unit_cost
        food.supplier = notes if notes and not food.supplier else food.supplier
        self._repo.flush()
        movement = self._record_stock_movement(
            farm_id=farm_id,
            food_id=food_id,
            movement_type="purchase",
            quantity=quantity,
            stock_before=stock_before,
            stock_after=food.current_stock,
            registered_by=user_id,
            unit_cost=unit_cost,
            total_cost=total_cost,
            notes=notes,
            movement_date=movement_date,
        )
        self._repo.commit()
        self._repo.refresh(food)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="stock_movement",
                           entity_id=str(movement.id),
                           details={"food_id": str(food_id), "type": "purchase",
                                    "quantity": str(quantity), "total_cost": str(total_cost)})
        self._repo.commit()
        return food, movement

    def record_stock_adjustment(
        self,
        farm_id: uuid.UUID,
        food_id: uuid.UUID,
        quantity: Decimal,
        reason: str,
        user_id: uuid.UUID,
        movement_date: datetime | None = None,
    ) -> tuple[Food, StockMovement]:
        """Ajuste manual (positivo suma, negativo resta). Nunca por debajo de 0."""
        food = self.get_food(farm_id, food_id)
        stock_before = food.current_stock
        new_stock = food.current_stock + quantity
        if new_stock < 0:
            raise BusinessRuleError(f"Cannot reduce stock below 0. Current: {food.current_stock}")
        food.current_stock = new_stock
        self._repo.flush()
        movement = self._record_stock_movement(
            farm_id=farm_id,
            food_id=food_id,
            movement_type="adjustment",
            quantity=quantity,
            stock_before=stock_before,
            stock_after=food.current_stock,
            registered_by=user_id,
            notes=reason,
            movement_date=movement_date,
        )
        self._repo.commit()
        self._repo.refresh(food)
        self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="stock_movement",
                           entity_id=str(movement.id),
                           details={"food_id": str(food_id), "type": "adjustment",
                                    "quantity": str(quantity), "reason": reason})
        self._repo.commit()
        return food, movement

    def get_stock_movements(
        self,
        farm_id: uuid.UUID,
        food_id: uuid.UUID | None = None,
        movement_type: str | None = None,
        limit: int = 100,
    ) -> Sequence[StockMovement]:
        return self._repo.list_movements(farm_id, food_id=food_id, movement_type=movement_type, limit=limit)


class CalfFeedingService:
    """Plan de alimentación de un ternero (HU007): qué alimento y cuánto por día.

    Vive en inventario porque lo que valida es un alimento de la finca. El
    ternero se consulta a ganado por un puerto (BovineLookup), así inventario
    depende de ganado y nunca al revés.
    """

    def __init__(self, repository: InventoryRepository, find_bovine: BovineLookup) -> None:
        self._repo = repository
        self._find_bovine = find_bovine

    def update_calf_feeding_plan(
        self,
        farm_id: uuid.UUID,
        bovine_id: uuid.UUID,
        food_id: uuid.UUID,
        quantity_kg_per_day: Decimal,
        start_date: date,
        end_date: date | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Valida y arma el plan (hoy no se guarda: ver la deuda en el README)."""
        if self._find_bovine(farm_id, bovine_id) is None:
            raise NotFoundError(CALF_NOT_FOUND)
        food = self._repo.get_food_in_farm(farm_id, food_id)
        if food is None:
            raise NotFoundError(FOOD_NOT_FOUND)
        if quantity_kg_per_day <= 0:
            raise BusinessRuleError(QUANTITY_NOT_POSITIVE)
        return {
            "bovine_id": str(bovine_id),
            "food_id": str(food_id),
            "food_name": food.name,
            "quantity_kg_per_day": float(quantity_kg_per_day),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "notes": notes,
        }
