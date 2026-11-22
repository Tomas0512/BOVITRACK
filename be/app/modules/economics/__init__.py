"""
Módulo economics — API pública (ingresos, egresos e indicadores de la finca).

`api_router` se carga solo cuando se pide, para no arrastrar la capa HTTP al
registrar el modelo (ver la explicación en app/modules/tasks/__init__.py).
"""

from typing import TYPE_CHECKING, Any

from app.modules.economics.schemas import EconomicIndicators, EconomicRecordResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["EconomicIndicators", "EconomicRecordResponse", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.economics.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
