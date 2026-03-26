"""
Módulo: schemas/milk_production.py
¿Qué? Schemas Pydantic para validar registros de producción lechera.
¿Para qué? Asegurar que cada ordeño tenga cantidad positiva y tipo válido
           antes de almacenarse en la base de datos.
¿Impacto? Datos de producción incorrectos afectan los reportes diarios
          (vista v_milk_production_daily) y las estadísticas de la finca.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class MilkProductionCreate(BaseModel):
    """¿Qué? Datos requeridos para registrar un ordeño.
    ¿Para qué? Registrar la producción asociada a un bovino y/o potrero.
    ¿Impacto? quantity_liters y milking_type son obligatorios y validados.
    """

    bovine_id: uuid.UUID | None = None
    land_plot_id: uuid.UUID | None = None
    milking_date: datetime
    quantity_liters: Decimal
    milking_type: str
    milking_session: str | None = None
    observations: str | None = None

    @field_validator("quantity_liters")
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        """¿Qué? Valida que la cantidad de litros sea mayor a 0.
        ¿Para qué? Un ordeño con 0 o litros negativos no tiene sentido.
        ¿Impacto? Evita datos basura en reportes de producción diaria.
        """
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v

    @field_validator("milking_type")
    @classmethod
    def validate_milking_type(cls, v: str) -> str:
        """¿Qué? Restringe el tipo de ordeño a 'manual' o 'mecanico'.
        ¿Para qué? Dato operativo que puede afectar análisis de eficiencia.
        ¿Impacto? Normaliza a minúsculas para consistencia en la BD.
        """
        allowed = {"manual", "mecanico"}
        if v.lower() not in allowed:
            raise ValueError(f"Tipo de ordeño inválido. Opciones: {', '.join(allowed)}")
        return v.lower()


class MilkProductionResponse(BaseModel):
    """¿Qué? Schema de respuesta para un registro de producción lechera.
    ¿Para qué? Definir la estructura JSON que retorna la API.
    ¿Impacto? Incluye registered_by para trazabilidad de quién registró el ordeño.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID | None
    land_plot_id: uuid.UUID | None
    milking_date: datetime
    quantity_liters: Decimal
    milking_type: str
    milking_session: str | None
    observations: str | None
    registered_by: uuid.UUID
    created_at: datetime
