import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


_INCOME_CATEGORIES = {
    "venta_leche", "venta_animal", "venta_cria", "subsidio", "otro_ingreso",
}
_EXPENSE_CATEGORIES = {
    "compra_insumo", "compra_animal", "servicio_veterinario",
    "transporte", "personal", "mantenimiento", "impuesto", "otro_gasto",
}


class EconomicRecordCreate(BaseModel):
    record_type: str
    category: str
    amount: Decimal
    record_date: date
    description: str | None = None
    reference_type: str | None = None
    reference_id: uuid.UUID | None = None

    @field_validator("record_type")
    @classmethod
    def validate_record_type(cls, v: str) -> str:
        allowed = {"ingreso", "egreso"}
        if v.lower() not in allowed:
            raise ValueError(f"Tipo invalido. Opciones: {', '.join(sorted(allowed))}")
        return v.lower()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v = v.lower()
        all_categories = _INCOME_CATEGORIES | _EXPENSE_CATEGORIES
        if v not in all_categories:
            raise ValueError(f"Categoria invalida. Opciones: {', '.join(sorted(all_categories))}")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class EconomicRecordUpdate(BaseModel):
    category: str | None = None
    amount: Decimal | None = None
    record_date: date | None = None
    description: str | None = None


class EconomicRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    record_type: str
    category: str
    amount: Decimal
    record_date: date
    description: str | None
    reference_type: str | None
    reference_id: uuid.UUID | None
    registered_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class EconomicIndicators(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    income_by_category: dict[str, Decimal]
    expense_by_category: dict[str, Decimal]
    monthly_income: Decimal
    monthly_expense: Decimal
    monthly_balance: Decimal
    avg_income_per_day: Decimal
    avg_expense_per_day: Decimal
