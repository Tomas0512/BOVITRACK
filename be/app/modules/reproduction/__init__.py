"""
Módulo reproduction — API pública (eventos reproductivos y registro de crías).

`api_router` se carga solo cuando se pide, para no arrastrar la capa HTTP al
registrar el modelo (ver la explicación en app/modules/tasks/__init__.py).
"""

from typing import TYPE_CHECKING, Any

from app.modules.reproduction.schemas import ReproductiveEventResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["ReproductiveEventResponse", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.reproduction.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
