"""
Módulo documents — API pública (gestión documental, HU012).

`api_router` se carga solo cuando se pide, para no arrastrar la capa HTTP al
registrar el modelo (ver la explicación en app/modules/tasks/__init__.py).
"""

from typing import TYPE_CHECKING, Any

from app.modules.documents.schemas import DocumentListResponse, DocumentResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["DocumentListResponse", "DocumentResponse", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.documents.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
