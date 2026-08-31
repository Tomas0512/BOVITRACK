"""
Módulo: schemas/land_plot.py
¿Qué? Schemas Pydantic para lotes (land_plot) dentro de una finca.
¿Para qué? Validar los datos al crear, actualizar y listar lotes.
¿Impacto? Sin estos schemas, se podrían crear lotes sin área o con capacidad negativa.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaddockNested(BaseModel):
    """¿Qué? Potrero que se crea junto con su lote.
    ¿Para qué? Un lote no puede quedar sin al menos un potrero.
    ¿Impacto? No lleva land_plot_id: lo hereda del lote que se está creando.
    """

    name: str
    area_hectares: Decimal
    max_capacity: int
    coverage_status: str = "bueno"
    pasture_type: str | None = None
    status: str = "libre"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre del potrero debe tener al menos 2 caracteres")
        return v

    @field_validator("area_hectares")
    @classmethod
    def validate_area(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El área del potrero debe ser mayor a 0")
        return v

    @field_validator("max_capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La capacidad del potrero debe ser mayor a 0")
        return v


class LandPlotCreate(BaseModel):
    name: str
    area: Decimal
    area_unit: str = "hectareas"
    usage_type: str
    max_capacity: int
    location: str | None = None
    # Obligatorio al crear: la jerarquía es finca > lote > potrero y un lote
    # sin potreros no representa nada utilizable. Se crean en la misma
    # transacción, así que o entran los dos o no entra ninguno.
    paddocks: list[PaddockNested] = Field(..., min_length=1)

    @field_validator("paddocks")
    @classmethod
    def validate_paddocks(cls, v: list[PaddockNested]) -> list[PaddockNested]:
        nombres = [p.name.lower() for p in v]
        if len(nombres) != len(set(nombres)):
            raise ValueError("Hay potreros repetidos: los nombres deben ser distintos")
        return v

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

    @field_validator("usage_type")
    @classmethod
    def validate_usage(cls, v: str) -> str:
        allowed = {"pastoreo", "cultivo", "reserva", "infraestructura", "otro"}
        if v not in allowed:
            raise ValueError("Tipo de uso inválido")
        return v


class LandPlotUpdate(BaseModel):
    name: str | None = None
    area: Decimal | None = None
    area_unit: str | None = None
    usage_type: str | None = None
    max_capacity: int | None = None
    location: str | None = None
    is_active: bool | None = None

    @field_validator("area")
    @classmethod
    def validate_area(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("El área debe ser mayor a 0")
        return v

    @field_validator("max_capacity")
    @classmethod
    def validate_capacity(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return v

    @field_validator("usage_type")
    @classmethod
    def validate_usage(cls, v: str | None) -> str | None:
        allowed = {"pastoreo", "cultivo", "reserva", "infraestructura", "otro"}
        if v is not None and v not in allowed:
            raise ValueError("Tipo de uso inválido")
        return v


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
