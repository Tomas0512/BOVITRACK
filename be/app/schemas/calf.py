"""
╔════════════════════════════════════════════════════════════════════════════╗
║ SCHEMAS: schemas/calf.py                                                  ║
║ PROPÓSITO: Validación Pydantic para datos de terneros                     ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Modelos Pydantic que definen la "forma" de los datos que entra y sale    ║
║   del API de terneros. Pydantic valida tipos, rangos y restricciones.     ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   1. Validar que los datos enviados por el cliente son correctos           ║
║   2. Documentar automáticamente en Swagger los campos esperados            ║
║   3. Serializar/deserializar entre JSON y Python                          ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   FastAPI retorna automáticamente HTTP 422 (Unprocessable Entity)         ║
║   si los datos no cumplen con los schemas.                                ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════
# 📥 SCHEMAS DE ENTRADA (REQUEST)
# ═══════════════════════════════════════════════════════════════════════════


class WeightRecordCreate(BaseModel):
    """
    ¿Qué? Schema para crear un nuevo registro de pesaje.

    ¿Para qué? Validar los datos cuando el usuario registra un pesaje.

    ¿Campos?
      - weight_kg: Peso en kilogramos (decimal, > 0)
      - measured_date: Fecha del pesaje (no puede ser futuro)
      - body_condition: Escala 1-5 (opcional)
      - observations: Observaciones libres (opcional)

    ¿Ejemplo?
      {
        "weight_kg": 45.5,
        "measured_date": "2026-06-15",
        "body_condition": 3,
        "observations": "Ternero en buen estado, ganancia normal"
      }
    """

    # Peso del ternero en kg
    # Nota: Decimal para precisión con números decimales
    weight_kg: Decimal = Field(
        ...,
        gt=0,  # Greater than 0
        decimal_places=2,
        description="Peso en kilogramos (ej: 45.50)",
    )

    # Fecha del pesaje
    measured_date: date = Field(
        ...,
        description="Fecha del pesaje (formato: YYYY-MM-DD)",
    )

    # Condición corporal (1=muy delgado, 5=muy gordo)
    body_condition: int | None = Field(
        None,
        ge=1,  # Greater than or equal
        le=5,  # Less than or equal
        description="Escala de condición corporal (1-5)",
    )

    # Notas adicionales
    observations: str | None = Field(
        None,
        max_length=500,
        description="Observaciones sobre el pesaje",
    )

    @field_validator("measured_date")
    @classmethod
    def validate_measured_date(cls, v: date) -> date:
        """
        ¿Qué? Valida que la fecha del pesaje no sea en el futuro.
        ¿Para qué? Evitar que se registren pesajes con fechas incorrectas.
        """
        if v > date.today():
            raise ValueError("La fecha del pesaje no puede ser en el futuro")
        return v

    class ConfigDict:
        """Configuración de Pydantic v2."""
        # Permite usar datetime.date directamente
        json_schema_extra = {
            "example": {
                "weight_kg": 45.50,
                "measured_date": "2026-06-15",
                "body_condition": 3,
                "observations": "Ganancia normal",
            }
        }


class CalfFeedingPlanCreate(BaseModel):
    """
    ¿Qué? Schema para crear un plan de alimentación.

    ¿Para qué? Validar datos cuando se registra qué come un ternero.

    ¿Campos?
      - food_id: UUID del alimento
      - quantity_kg_per_day: Cantidad diaria en kg
      - start_date: Fecha de inicio del plan
      - end_date: Fecha de fin (opcional)
      - notes: Observaciones
    """

    food_id: uuid.UUID = Field(..., description="ID del alimento")

    quantity_kg_per_day: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Cantidad diaria en kg",
    )

    start_date: date = Field(..., description="Fecha de inicio del plan")

    end_date: date | None = Field(None, description="Fecha de fin (opcional)")

    notes: str | None = Field(
        None,
        max_length=500,
        description="Notas sobre el plan de alimentación",
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info) -> date | None:
        """
        ¿Qué? Valida que end_date >= start_date.
        """
        if v and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("La fecha de fin debe ser >= a la de inicio")
        return v


# ═══════════════════════════════════════════════════════════════════════════
# 📤 SCHEMAS DE SALIDA (RESPONSE)
# ═══════════════════════════════════════════════════════════════════════════


class WeightRecordResponse(BaseModel):
    """
    ¿Qué? Schema para retornar un registro de pesaje al cliente.

    ¿Para qué? Serializar el pesaje como JSON en la respuesta HTTP.

    ¿Campos?
      - id: UUID del registro
      - date: Fecha del pesaje (string ISO)
      - weight_kg: Peso en kg (float)
      - daily_gain_kg: Ganancia diaria calculada (float o null)
    """

    id: uuid.UUID = Field(..., description="ID único del pesaje")

    date: str = Field(..., description="Fecha en formato ISO (YYYY-MM-DD)")

    weight_kg: float = Field(..., description="Peso en kilogramos")

    daily_gain_kg: float | None = Field(
        None,
        description="Ganancia diaria (kg/día) respecto al pesaje anterior",
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2026-06-15",
                "weight_kg": 45.5,
                "daily_gain_kg": 0.25,
            }
        }


class CalfListResponse(BaseModel):
    """
    ¿Qué? Schema para listar terneros (vista simplificada).

    ¿Para qué? Retornar un array de terneros para la lista (CalfList.tsx).

    ¿Campos?
      - id, identification_number, name, sex, birth_date
      - current_weight_kg, age_days
    """

    id: uuid.UUID
    identification_number: str
    name: str | None
    sex: str
    birth_date: date
    current_weight_kg: float
    age_days: int


class CalfMetricsData(BaseModel):
    """
    ¿Qué? Schema para los indicadores de crecimiento.

    ¿Para qué? Retornar métricas calculadas en get_calf_details.
    """

    current_weight_kg: float = Field(..., description="Peso actual en kg")

    birth_weight_kg: float | None = Field(None, description="Peso al nacer en kg")

    days_old: int = Field(..., description="Edad en días")

    daily_gain_kg: float | None = Field(
        None,
        description="Ganancia promedio diaria en kg",
    )

    expected_weight_kg: float = Field(..., description="Peso esperado según edad/raza")

    growth_percentage: float = Field(
        ...,
        description="Porcentaje de cumplimiento (actual/esperado × 100)",
    )

    feeding_plan: str | None = Field(..., description="Plan de alimentación recomendado")


class CalfGrowthMetricsResponse(BaseModel):
    """
    ¿Qué? Schema para retornar un ternero con todas sus métricas.

    ¿Para qué? Usar en el detalle del ternero (BovineDetailPage).

    ¿Contiene?
      - bovine: Datos del bovino (BovineResponse)
      - metrics: Indicadores de crecimiento (CalfMetricsData)
    """

    # Nota: BovineResponse se importa de bovine.py
    bovine: dict = Field(..., description="Datos del ternero")

    metrics: dict = Field(..., description="Métricas de crecimiento")


class CalfSummaryResponse(BaseModel):
    """
    ¿Qué? Schema para el resumen global de terneros en una finca.

    ¿Para qué? Dashboard con estadísticas (HU007 Task 7.3).

    ¿Campos?
      - total_calves: Total de terneros
      - calves_0_30_days: Terneros de 0-30 días
      - calves_31_90_days: Terneros de 31-90 días
      - calves_91_365_days: Terneros de 91-365 días
      - average_weight_kg: Peso promedio
      - average_daily_gain: Ganancia diaria promedio
    """

    total_calves: int = Field(..., description="Total de terneros activos")

    calves_0_30_days: int = Field(..., description="Terneros de 0 a 30 días")

    calves_31_90_days: int = Field(..., description="Terneros de 31 a 90 días")

    calves_91_365_days: int = Field(..., description="Terneros de 91 a 365 días")

    average_weight_kg: float = Field(..., description="Peso promedio en kg")

    average_daily_gain: float = Field(..., description="Ganancia diaria promedio")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "total_calves": 12,
                "calves_0_30_days": 2,
                "calves_31_90_days": 4,
                "calves_91_365_days": 6,
                "average_weight_kg": 95.5,
                "average_daily_gain": 0.65,
            }
        }
