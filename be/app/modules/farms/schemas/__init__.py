"""Schemas de farms: fincas y catálogos, lotes y potreros."""

from app.modules.farms.schemas.farm import (
    CityOption,
    DepartmentOption,
    FarmBulkCreateRequest,
    FarmBulkCreateResult,
    FarmBulkError,
    FarmCreate,
    FarmResponse,
    FarmUpdate,
    PurposeOption,
)
from app.modules.farms.schemas.land_plot import LandPlotCreate, LandPlotResponse, LandPlotUpdate, PaddockNested
from app.modules.farms.schemas.paddock import BovineRef, PaddockCreate, PaddockResponse, PaddockUpdate

__all__ = [
    "BovineRef",
    "CityOption",
    "DepartmentOption",
    "FarmBulkCreateRequest",
    "FarmBulkCreateResult",
    "FarmBulkError",
    "FarmCreate",
    "FarmResponse",
    "FarmUpdate",
    "LandPlotCreate",
    "LandPlotResponse",
    "LandPlotUpdate",
    "PaddockCreate",
    "PaddockNested",
    "PaddockResponse",
    "PaddockUpdate",
    "PurposeOption",
]
