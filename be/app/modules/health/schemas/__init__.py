"""
Contrato de entrada y salida del módulo health (tratamientos y planes sanitarios).
"""

from app.modules.health.schemas.sanitary_plan import (
    SanitaryPlanCreate,
    SanitaryPlanResponse,
    SanitaryPlanUpdate,
)
from app.modules.health.schemas.treatment import TreatmentCreate, TreatmentResponse

__all__ = [
    "SanitaryPlanCreate",
    "SanitaryPlanResponse",
    "SanitaryPlanUpdate",
    "TreatmentCreate",
    "TreatmentResponse",
]
