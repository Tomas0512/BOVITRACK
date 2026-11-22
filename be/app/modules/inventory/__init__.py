"""
Módulo inventory — API pública (alimentos, consumos y movimientos de stock, HU011).

Además de `api_router`, ofrece a otros módulos las implementaciones de los
puertos que el inventario sabe responder:
  - build_low_stock_lookup(db) -> LowStockLookup   (lo usa notifications)
  - build_food_lookup(db)      -> ¿alimento de la finca? (lo usa health)

Todo se carga solo cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

from app.modules.inventory.schemas import FoodResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    from app.modules.inventory.dependencies import build_food_lookup, build_low_stock_lookup

    api_router: APIRouter

__all__ = ["FoodResponse", "api_router", "build_food_lookup", "build_low_stock_lookup"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.inventory.router import module_router

        return module_router
    if name in ("build_low_stock_lookup", "build_food_lookup"):
        from app.modules.inventory import dependencies

        return getattr(dependencies, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
