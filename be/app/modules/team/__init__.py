"""
Módulo team — API pública (el equipo de una finca: empleados, invitaciones y
reactivación de cuentas).

Es un módulo consumidor: usa a identity (usuarios, roles, membresías) y a farms
(nombre de la finca), y ningún otro módulo depende de él. Solo ofrece api_router,
que se carga cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.team.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
