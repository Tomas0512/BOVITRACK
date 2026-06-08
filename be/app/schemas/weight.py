"""
Módulo: schemas/weight.py
¿Qué? Schemas Pydantic para validar entrada y salida de pesajes de bovinos.
¿Para qué? Garantizar que los datos enviados al API cumplan con los tipos y
           restricciones antes de llegar a la base de datos.
¿Impacto? Sin estos schemas, pesos negativos o fechas futuras podrían
          insertarse directamente, generando datos incoherentes en el historial.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class WeightCreate(BaseModel):
    """
    ¿Qué? Valida los datos al registrar un nuevo pesaje de un bovino.
    ¿Para qué? Asegurar que el peso sea positivo y la fecha no sea futura.
    ¿Impacto? Rechaza peticiones inválidas con mensajes claros antes de
              tocar la base de datos.
    """
    weight_kg: Decimal
    measured_at: date
    body_condition: int | None = None   # escala 1-5
    observations: str | None = None

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: Decimal) -> Decimal:
        """¿Qué? Valida que el peso sea mayor a 0.
        ¿Para qué? Un peso de 0 o negativo no tiene sentido biológico.
        """
        if v <= 0:
            raise ValueError("El peso debe ser mayor a 0 kg.")
        return v

    @field_validator("measured_at")
    @classmethod
    def validate_date(cls, v: date) -> date:
        """¿Qué? Valida que la fecha del pesaje no sea futura.
        ¿Para qué? No se puede registrar un peso de una fecha que no ha ocurrido.
        """
        from datetime import date as date_type
        if v > date_type.today():
            raise ValueError("La fecha del pesaje no puede ser futura.")
        return v

    @field_validator("body_condition")
    @classmethod
    def validate_body_condition(cls, v: int | None) -> int | None:
        """¿Qué? Valida que la condición corporal esté en escala 1-5.
        ¿Para qué? La escala de condición corporal bovina es estándar 1-5.
        """
        if v is not None and v not in range(1, 6):
            raise ValueError("La condición corporal debe estar entre 1 y 5.")
        return v


class WeightResponse(BaseModel):
    """
    ¿Qué? Datos que devuelve el API al consultar un pesaje.
    ¿Para qué? Controlar exactamente qué campos se exponen al frontend,
               evitando filtrar datos internos innecesarios.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID
    weight_kg: Decimal
    measured_at: date
    daily_gain: Decimal | None
    body_condition: int | None
    observations: str | None
    registered_by: uuid.UUID
    synchronized: bool
    created_at: datetime
