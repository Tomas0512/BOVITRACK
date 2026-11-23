"""
Contrato de entrada y salida del módulo livestock: bovinos, pesajes, terneros y movimientos.
"""

from app.modules.livestock.schemas.bovine import BovineCreate, BovineResponse, BovineUpdate
from app.modules.livestock.schemas.calf import (
    CalfGrowthMetricsResponse,
    CalfListResponse,
    CalfMetricsData,
    CalfSummaryResponse,
    WeightRecordCreate,
    WeightRecordResponse,
)
from app.modules.livestock.schemas.movement import MovementCreate, MovementResponse, MovementUpdate
from app.modules.livestock.schemas.weight import WeightCreate, WeightResponse

__all__ = [
    "BovineCreate",
    "BovineResponse",
    "BovineUpdate",
    "CalfGrowthMetricsResponse",
    "CalfListResponse",
    "CalfMetricsData",
    "CalfSummaryResponse",
    "MovementCreate",
    "MovementResponse",
    "MovementUpdate",
    "WeightCreate",
    "WeightRecordCreate",
    "WeightRecordResponse",
    "WeightResponse",
]
