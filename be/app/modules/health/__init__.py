"""
Módulo health — API pública (tratamientos aplicados y planes sanitarios).

Además de `api_router` (que incluye los endpoints de tratamientos y de planes),
ofrece a otros módulos:
  - build_sanitary_alerts(db) -> SanitaryAlertsSource   (lo usa notifications)

Todo se carga solo cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

from app.modules.health.schemas import SanitaryPlanResponse, TreatmentResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    from app.modules.health.dependencies import build_sanitary_alerts

    api_router: APIRouter

__all__ = ["SanitaryPlanResponse", "TreatmentResponse", "api_router", "build_sanitary_alerts"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.health.router import router

        return router
    if name == "build_sanitary_alerts":
        from app.modules.health.dependencies import build_sanitary_alerts

        return build_sanitary_alerts
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
