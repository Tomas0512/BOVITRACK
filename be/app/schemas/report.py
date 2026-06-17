from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ReportCategory(str, Enum):
    PRODUCTIVE = "productivo"
    SANITARY = "sanitario"
    ECONOMIC = "economico"


class ExportFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"


class ReportFilterParams(BaseModel):
    category: ReportCategory | None = Field(None, description="Filter by category")
    start_date: date | None = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: date | None = Field(None, description="End date (YYYY-MM-DD)")
    export: ExportFormat = Field(ExportFormat.JSON, description="Export format")


class ProductiveReport(BaseModel):
    total_bovines: int = 0
    males: int = 0
    females: int = 0
    avg_weight: float | None = None
    total_milk_liters: float = 0
    avg_milk_per_day: float = 0
    total_calves: int = 0
    calves_by_age_group: dict[str, int] = {}


class SanitaryReport(BaseModel):
    total_treatments: int = 0
    active_sanitary_plans: int = 0
    pending_treatments: int = 0
    treatments_by_type: dict[str, int] = {}


class EconomicReport(BaseModel):
    total_income: float = 0
    total_expense: float = 0
    balance: float = 0
    income_by_activity: dict[str, float] = {}
    expense_by_activity: dict[str, float] = {}


class ReportResponse(BaseModel):
    farm_id: UUID
    farm_name: str
    category: ReportCategory | None
    start_date: date | None
    end_date: date | None
    productive: ProductiveReport | None = None
    sanitary: SanitaryReport | None = None
    economic: EconomicReport | None = None
