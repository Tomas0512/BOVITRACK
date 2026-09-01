import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.movement import MOVEMENT_TYPES


class MovementCreate(BaseModel):
    bovine_id: uuid.UUID | None = None
    animal_identifier: str | None = None
    movement_type: str
    movement_date: date
    price: Decimal | None = None
    counterparty_name: str | None = None
    counterparty_document: str | None = None
    counterparty_phone: str | None = None
    origin_farm_name: str | None = None
    destination_farm_name: str | None = None
    reason: str | None = None
    observations: str | None = None

    @field_validator("movement_type")
    @classmethod
    def validate_movement_type(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in MOVEMENT_TYPES:
            raise ValueError(f"Tipo de movimiento inválido. Opciones: {', '.join(sorted(MOVEMENT_TYPES))}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @model_validator(mode="after")
    def validate_date(self) -> "MovementCreate":
        if self.movement_date > date.today():
            raise ValueError("La fecha del movimiento no puede ser futura")
        return self


class MovementUpdate(BaseModel):
    bovine_id: uuid.UUID | None = None
    animal_identifier: str | None = None
    movement_type: str | None = None
    movement_date: date | None = None
    price: Decimal | None = None
    counterparty_name: str | None = None
    counterparty_document: str | None = None
    counterparty_phone: str | None = None
    origin_farm_name: str | None = None
    destination_farm_name: str | None = None
    reason: str | None = None
    observations: str | None = None


class MovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID | None
    animal_identifier: str | None
    movement_type: str
    movement_date: date
    price: Decimal | None
    counterparty_name: str | None
    counterparty_document: str | None
    counterparty_phone: str | None
    origin_farm_name: str | None
    destination_farm_name: str | None
    reason: str | None
    observations: str | None
    registered_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
