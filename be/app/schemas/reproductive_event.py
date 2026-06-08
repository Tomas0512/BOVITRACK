import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ReproductiveEventCreate(BaseModel):
    bovine_id: uuid.UUID
    event_type: str
    event_date: date
    result: str | None = None
    due_date: date | None = None
    bull_id: uuid.UUID | None = None
    calf_id: uuid.UUID | None = None
    observations: str | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        allowed = {"servicio", "diagnostico_gestion", "parto", "aborto", "secado"}
        if v.lower() not in allowed:
            raise ValueError(f"Tipo de evento inválido. Opciones: {', '.join(sorted(allowed))}")
        return v.lower()

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"positivo", "negativo", "gemelos", "macho", "hembra"}
        if v.lower() not in allowed:
            raise ValueError(f"Resultado inválido. Opciones: {', '.join(sorted(allowed))}")
        return v.lower()


class ReproductiveEventUpdate(BaseModel):
    event_type: str | None = None
    event_date: date | None = None
    result: str | None = None
    due_date: date | None = None
    bull_id: uuid.UUID | None = None
    calf_id: uuid.UUID | None = None
    observations: str | None = None


class ReproductiveEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID
    event_type: str
    event_date: date
    result: str | None
    due_date: date | None
    bull_id: uuid.UUID | None
    calf_id: uuid.UUID | None
    observations: str | None
    registered_by: uuid.UUID
    created_at: datetime
