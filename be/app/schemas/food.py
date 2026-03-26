"""
Módulo: schemas/food.py
¿Qué? Schemas Pydantic para validar datos de alimentos (inventario) y consumos.
¿Para qué? Controlar el registro de insumos alimentarios y su consumo por
           bovinos/potreros, validando stock y cantidades.
¿Impacto? Sin estas validaciones, el sistema permitiría registrar consumos
          con cantidades negativas o nombres vacíos, corrompiendo el inventario.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class FoodCreate(BaseModel):
    """¿Qué? Datos requeridos para registrar un alimento en el inventario.
    ¿Para qué? Cada finca mantiene su propio catálogo de alimentos con stock.
    ¿Impacto? El nombre debe tener al menos 2 caracteres para evitar registros vacíos.
    """

    name: str
    category: str
    unit_of_measure: str
    current_stock: Decimal = Decimal("0")
    min_stock_alert: Decimal | None = None
    cost_per_unit: Decimal | None = None
    expiration_date: date | None = None
    supplier: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """¿Qué? Valida que el nombre del alimento tenga al menos 2 caracteres.
        ¿Para qué? Evitar registros con nombres vacíos o de un solo carácter.
        ¿Impacto? Mejora la calidad de datos en el inventario.
        """
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v


class FoodUpdate(BaseModel):
    """¿Qué? Schema para actualización parcial de un alimento.
    ¿Para qué? Permitir actualizar stock, precio, proveedor, etc. sin reenviar todo.
    ¿Impacto? Todos los campos son opcionales — solo se actualizan los enviados.
    """

    name: str | None = None
    category: str | None = None
    unit_of_measure: str | None = None
    current_stock: Decimal | None = None
    min_stock_alert: Decimal | None = None
    cost_per_unit: Decimal | None = None
    expiration_date: date | None = None
    supplier: str | None = None


class FoodResponse(BaseModel):
    """¿Qué? Schema de respuesta para un alimento del inventario.
    ¿Para qué? Controlar la estructura JSON que retorna la API.
    ¿Impacto? Incluye current_stock y min_stock_alert para que el frontend
              pueda mostrar alertas de stock bajo.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    category: str
    unit_of_measure: str
    current_stock: Decimal
    min_stock_alert: Decimal | None
    cost_per_unit: Decimal | None
    expiration_date: date | None
    supplier: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConsumptionCreate(BaseModel):
    """¿Qué? Datos requeridos para registrar el consumo de un alimento.
    ¿Para qué? Descontar stock del inventario y registrar quién consumió qué.
    ¿Impacto? El service valida que haya stock suficiente antes de registrar.
              Si no hay stock, retorna 400 Bad Request.
    """

    land_plot_id: uuid.UUID | None = None
    bovine_id: uuid.UUID | None = None
    food_id: uuid.UUID
    quantity: Decimal
    feeding_date: datetime
    observations: str | None = None

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        """¿Qué? Valida que la cantidad consumida sea mayor a 0.
        ¿Para qué? Un consumo de 0 o negativo no tiene sentido operativo.
        ¿Impacto? Previene descontrol del inventario.
        """
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class ConsumptionResponse(BaseModel):
    """¿Qué? Schema de respuesta para un registro de consumo.
    ¿Para qué? Incluye todos los campos necesarios para el historial de consumos.
    ¿Impacto? registered_by permite auditar quién registró cada consumo.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    land_plot_id: uuid.UUID | None
    bovine_id: uuid.UUID | None
    food_id: uuid.UUID
    quantity: Decimal
    feeding_date: datetime
    observations: str | None
    registered_by: uuid.UUID
    created_at: datetime
