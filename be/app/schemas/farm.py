import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class FarmCreate(BaseModel):
    """Schema para crear una finca."""

    name: str
    address: str
    department_id: uuid.UUID
    city_municipality: str
    total_area: Decimal
    area_unit: str = "hectareas"
    purpose_id: uuid.UUID
    farm_identifier: str
    phone: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        if len(v) > 255:
            raise ValueError("El nombre no puede exceder 255 caracteres")
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("La dirección debe tener al menos 5 caracteres")
        if len(v) > 500:
            raise ValueError("La dirección no puede exceder 500 caracteres")
        return v

    @field_validator("city_municipality")
    @classmethod
    def validate_city_municipality(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Ciudad o municipio debe tener al menos 2 caracteres")
        if len(v) > 120:
            raise ValueError("Ciudad o municipio no puede exceder 120 caracteres")
        return v

    @field_validator("farm_identifier")
    @classmethod
    def validate_farm_identifier(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El identificador debe tener al menos 3 caracteres")
        if len(v) > 100:
            raise ValueError("El identificador no puede exceder 100 caracteres")
        return v

    @field_validator("total_area")
    @classmethod
    def validate_total_area(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El área total debe ser mayor a 0")
        return v

    @field_validator("area_unit")
    @classmethod
    def validate_area_unit(cls, v: str) -> str:
        allowed = {"hectareas", "metros_cuadrados", "fanegadas"}
        if v not in allowed:
            raise ValueError(f"Unidad de área inválida. Opciones: {', '.join(allowed)}")
        return v


class FarmResponse(BaseModel):
    """Schema de respuesta para una finca."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    address: str
    department_id: uuid.UUID
    city_municipality: str
    total_area: Decimal
    area_unit: str
    purpose_id: uuid.UUID
    farm_identifier: str
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FarmUpdate(BaseModel):
    """Schema para actualizar una finca."""

    name: str
    address: str
    department_id: uuid.UUID
    city_municipality: str
    total_area: Decimal
    area_unit: str = "hectareas"
    purpose_id: uuid.UUID
    farm_identifier: str
    phone: str | None = None


class FarmBulkCreateRequest(BaseModel):
    items: list[FarmCreate]


class DepartmentOption(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str | None


class PurposeOption(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
