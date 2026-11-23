"""
Módulo reports — API pública (estadísticas y reportes exportables).

`api_router` se carga solo cuando se pide (mismo patrón que los demás módulos).
Este módulo no tiene tablas propias: es un modelo de lectura sobre vistas SQL.
"""

from typing import TYPE_CHECKING, Any

from app.modules.reports.schemas import ReportResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["ReportResponse", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.reports.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
