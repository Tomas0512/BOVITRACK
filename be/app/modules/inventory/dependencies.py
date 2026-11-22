"""
Módulo: modules/inventory/dependencies.py (composición del módulo)
¿Qué? Dos responsabilidades de "cableado":
      1. Arma el InventoryService de cada request con sus colaboradores.
      2. Ofrece a OTROS módulos las implementaciones de los puertos que el
         inventario sabe responder (stock bajo, ¿este alimento es de la finca?).
¿Para qué? Que la definición de "stock bajo" viva en un solo lugar: el módulo
           dueño de los datos. Notificaciones y salud no consultan la tabla
           food; piden la respuesta por un puerto.
¿Impacto? Los consumidores importan solo `app.modules.inventory` (API pública)
          desde su propio dependencies.py; import-linter impide que entren a
          los internos o que el inventario dependa de ellos (capas de módulos).
"""

import uuid
from collections.abc import Callable
from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms, livestock
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import CalfFeedingService, InventoryService
from app.shared.ports import LowStockItem, LowStockLookup

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Dependencia de FastAPI: un InventoryService por request."""
    return InventoryService(
        repository=InventoryRepository(db),
        ensure_farm_scope=farms.build_farm_scope_checker(db, find_bovine=livestock.build_bovine_lookup(db)),
        find_paddock=farms.build_paddock_lookup(db),
        record_audit=partial(add_audit_log, db),
    )


def get_calf_feeding_service(db: Session = Depends(get_db)) -> CalfFeedingService:
    """Dependencia de FastAPI: plan de alimentación de terneros."""
    return CalfFeedingService(InventoryRepository(db), livestock.build_bovine_lookup(db))


# ── Puertos que el inventario ofrece a otros módulos ──────────────


def build_low_stock_lookup(db: Session) -> LowStockLookup:
    """LowStockLookup: insumos activos en stock bajo, del menor stock al mayor."""
    repo = InventoryRepository(db)

    def lookup(farm_id: uuid.UUID) -> list[LowStockItem]:
        return [
            LowStockItem(
                id=f.id,
                name=f.name,
                category=f.category,
                current_stock=f.current_stock,
                min_stock_alert=f.min_stock_alert,
                unit_of_measure=f.unit_of_measure,
            )
            for f in repo.low_stock_by_quantity(farm_id)
        ]

    return lookup


def build_food_lookup(db: Session) -> Callable[[uuid.UUID, uuid.UUID], bool]:
    """¿El alimento existe y es de la finca? (lo usa salud al registrar tratamientos)."""
    repo = InventoryRepository(db)

    def exists(farm_id: uuid.UUID, food_id: uuid.UUID) -> bool:
        return repo.get_food_in_farm(farm_id, food_id) is not None

    return exists
