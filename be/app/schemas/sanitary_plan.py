"""
Módulo: schemas/sanitary_plan.py
¿Qué? Schemas Pydantic para validar datos de planes sanitarios.
¿Para qué? Controlar el registro de vacunas y tratamientos programados.
¿Impacto? Sin validaciones, permitiría registrar planes inconsistentes
          con fechas inválidas o frecuencias negativas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class SanitaryPlanCreate(BaseModel):
    """¿Qué? Datos requeridos para crear un plan sanitario.
    ¿Para qué? Registrar qué vacunas/tratamientos debe recibir un bovino o lote.
    ¿Impacto? Al menos uno de bovine_id o land_plot_id debe estar presente.
    """

    bovine_id: uuid.UUID | None = None
    land_plot_id: uuid.UUID | None = None
    vaccine_or_treatment_name: str
    treatment_type: str  # "vacuna", "desparasitación", "suplemento", etc.
    administration_route: str  # "intramuscular", "oral", "tópica", etc.
    dose: str | None = None  # "2 mL", "100 mL", etc.
    frequency_days: int  # Cada cuántos días: 180, 90, 30, etc.
    next_scheduled_date: datetime | None = None
    observations: str | None = None

    @field_validator("vaccine_or_treatment_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v

    @field_validator("frequency_days")
    @classmethod
    def validate_frequency(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La frecuencia debe ser mayor a 0 días")
        return v

    @field_validator("bovine_id", "land_plot_id", mode="before")
    @classmethod
    def at_least_one_target(cls, v, info):
        """¿Qué? Valida que al menos uno de bovine_id o land_plot_id esté presente.
        ¿Para qué? Asegurar que el plan sanitario tiene un objetivo (bovino o lote).
        """
        if info.field_name == "bovine_id" and v is None:
            land_plot_id = info.data.get("land_plot_id")
            if land_plot_id is None:
                raise ValueError("Debe especificar bovine_id o land_plot_id")
        return v


class SanitaryPlanUpdate(BaseModel):
    """¿Qué? Schema para actualización parcial de un plan sanitario.
    ¿Para qué? Permitir actualizar fechas, observaciones, estado sin reenviar todo.
    ¿Impacto? Solo se actualizan los campos enviados.
    """

    vaccine_or_treatment_name: str | None = None
    treatment_type: str | None = None
    administration_route: str | None = None
    dose: str | None = None
    frequency_days: int | None = None
    last_applied_date: datetime | None = None
    next_scheduled_date: datetime | None = None
    is_active: bool | None = None
    observations: str | None = None


class SanitaryPlanResponse(BaseModel):
    """¿Qué? Schema de respuesta para un plan sanitario.
    ¿Para qué? Controlar la estructura JSON que retorna la API.
    ¿Impacto? Incluye todas las fechas para que el frontend pueda mostrar
              alertas y calendarios sanitarios.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID | None
    land_plot_id: uuid.UUID | None
    vaccine_or_treatment_name: str
    treatment_type: str
    administration_route: str
    dose: str | None
    frequency_days: int
    last_applied_date: datetime | None
    next_scheduled_date: datetime | None
    is_active: bool
    observations: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
