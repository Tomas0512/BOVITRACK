"""
Módulo audit — API pública (consulta y exportación de la auditoría, HU015).

Registrar auditoría NO es de este módulo: es infraestructura transversal en
app.core.audit_trail (cualquier módulo la usa sin depender de este).
`api_router` se carga solo cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

from app.modules.audit.schemas import AuditLogPage, AuditLogResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["AuditLogPage", "AuditLogResponse", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.audit.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
