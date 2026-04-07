"""
Módulo: schemas/land_plot.py
¿Qué? Schemas Pydantic para lotes (land_plot) dentro de una finca.
¿Para qué? Validar los datos al crear, actualizar y listar lotes.
¿Impacto? Sin estos schemas, se podrían crear lotes sin área o con capacidad negativa.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class LandPlotCreate(BaseModel):
    name: str
    area: Decimal
    area_unit: str = "hectareas"
    usage_type: str
    max_capacity: int
    location: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v

    @field_validator("area")
    @classmethod
    def validate_area(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El área debe ser mayor a 0")
        return v

    @field_validator("max_capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return v


class LandPlotUpdate(BaseModel):
    name: str | None = None
    area: Decimal | None = None
    area_unit: str | None = None
    usage_type: str | None = None
    max_capacity: int | None = None
    location: str | None = None
    is_active: bool | None = None


class LandPlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    area: Decimal
    area_unit: str
    usage_type: str
    max_capacity: int
    location: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
