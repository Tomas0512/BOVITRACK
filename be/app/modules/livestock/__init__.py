"""
Módulo livestock — API pública (bovinos, pesajes, terneros y movimientos).

Además de `api_router` (que incluye los cuatro routers del módulo), ofrece a
otros módulos los puertos que el ganado sabe responder:
  - build_bovine_lookup(db)  -> BovineLookup  (milk_production, reproduction,
                                                documents, health)
  - build_calf_registrar(db) -> CalfRegistrar (reproduction)

Todo se carga solo cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

from app.modules.livestock.schemas import BovineResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    from app.modules.livestock.dependencies import build_bovine_lookup, build_calf_registrar

    api_router: APIRouter

__all__ = ["BovineResponse", "api_router", "build_bovine_lookup", "build_calf_registrar"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.livestock.router import router

        return router
    if name in ("build_bovine_lookup", "build_calf_registrar"):
        from app.modules.livestock import dependencies

        return getattr(dependencies, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
