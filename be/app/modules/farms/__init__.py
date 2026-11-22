"""
Módulo farms — API pública (fincas, lotes, potreros y catálogos geográficos).

Está justo encima de identity en las capas: lo usan livestock, inventory, health
y los demás; farms solo usa a identity.

Lo que ofrece a otros módulos (puertos):
  - build_farm_scope_checker(db, find_bovine=...) -> FarmScopeChecker
  - build_land_plot_lookup(db)    -> LandPlotLookup
  - build_paddock_lookup(db)      -> PaddockLookup
  - build_land_plot_id_by_name(db), build_paddock_id_by_name(db) -> búsqueda por nombre
  - list_active_farm_ids(db)      -> ids de las fincas activas
  - build_farm_name_lookup(db)    -> nombre de una finca (team)
  - api_router (se carga solo cuando se pide, mismo patrón que los demás módulos)
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter

    from app.modules.farms.dependencies import (
        build_farm_name_lookup,
        build_farm_scope_checker,
        build_land_plot_id_by_name,
        build_land_plot_lookup,
        build_paddock_id_by_name,
        build_paddock_lookup,
        list_active_farm_ids,
    )

    api_router: APIRouter

_PROVIDERS = (
    "build_farm_name_lookup",
    "build_farm_scope_checker",
    "build_land_plot_id_by_name",
    "build_land_plot_lookup",
    "build_paddock_id_by_name",
    "build_paddock_lookup",
    "list_active_farm_ids",
)

__all__ = [
    "api_router",
    "build_farm_name_lookup",
    "build_farm_scope_checker",
    "build_land_plot_id_by_name",
    "build_land_plot_lookup",
    "build_paddock_id_by_name",
    "build_paddock_lookup",
    "list_active_farm_ids",
]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.farms.router import router

        return router
    if name in _PROVIDERS:
        from app.modules.farms import dependencies

        return getattr(dependencies, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
