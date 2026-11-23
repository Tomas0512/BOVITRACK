"""
Módulo: modules/inventory/repository.py
¿Qué? Acceso a datos del inventario: alimentos, consumos y movimientos de stock.
¿Para qué? Que el servicio pida "el alimento X de la finca" o "los insumos en
           stock bajo" sin escribir consultas.
¿Impacto? Toda consulta filtra por farm_id.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.inventory.models import Consumption, Food, StockMovement


class InventoryRepository:
    """Repositorio del inventario sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Alimentos ────────────────────────────────────────────

    def get_food_in_farm(self, farm_id: uuid.UUID, food_id: uuid.UUID) -> Food | None:
        """El alimento si es de la finca (activo o no); si no, None."""
        stmt = select(Food).where(Food.id == food_id, Food.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_active_foods(self, farm_id: uuid.UUID) -> Sequence[Food]:
        """Alimentos activos ordenados por nombre."""
        stmt = select(Food).where(Food.farm_id == farm_id, Food.is_active.is_(True)).order_by(Food.name.asc())
        return self._db.execute(stmt).scalars().all()

    def _low_stock_stmt(self, farm_id: uuid.UUID) -> Select:
        return select(Food).where(
            Food.farm_id == farm_id,
            Food.is_active.is_(True),
            Food.min_stock_alert.isnot(None),
            Food.current_stock <= Food.min_stock_alert,
        )

    def low_stock_by_ratio(self, farm_id: uuid.UUID) -> Sequence[Food]:
        """Stock bajo, del más crítico (stock/mínimo más chico) al menos crítico."""
        stmt = self._low_stock_stmt(farm_id).order_by(
            (Food.current_stock / func.nullif(Food.min_stock_alert, 0)).asc()
        )
        return self._db.execute(stmt).scalars().all()

    def low_stock_by_quantity(self, farm_id: uuid.UUID) -> Sequence[Food]:
        """Stock bajo, del menor stock al mayor (orden del banner de alertas)."""
        stmt = self._low_stock_stmt(farm_id).order_by(Food.current_stock.asc())
        return self._db.execute(stmt).scalars().all()

    # ── Consumos y movimientos ───────────────────────────────

    def list_consumptions(
        self, farm_id: uuid.UUID, *, food_id: uuid.UUID | None = None, bovine_id: uuid.UUID | None = None
    ) -> Sequence[Consumption]:
        stmt = select(Consumption).where(Consumption.farm_id == farm_id)
        if food_id:
            stmt = stmt.where(Consumption.food_id == food_id)
        if bovine_id:
            stmt = stmt.where(Consumption.bovine_id == bovine_id)
        return self._db.execute(stmt.order_by(Consumption.feeding_date.desc())).scalars().all()

    def list_movements(
        self,
        farm_id: uuid.UUID,
        *,
        food_id: uuid.UUID | None = None,
        movement_type: str | None = None,
        limit: int = 100,
    ) -> Sequence[StockMovement]:
        stmt = select(StockMovement).where(StockMovement.farm_id == farm_id)
        if food_id:
            stmt = stmt.where(StockMovement.food_id == food_id)
        if movement_type:
            stmt = stmt.where(StockMovement.movement_type == movement_type)
        stmt = stmt.order_by(StockMovement.movement_date.desc()).limit(limit)
        return self._db.execute(stmt).scalars().all()

    # ── Unidad de trabajo ────────────────────────────────────

    def add(self, row: Food | Consumption | StockMovement) -> None:
        self._db.add(row)

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, row: Food | Consumption | StockMovement) -> None:
        self._db.refresh(row)
