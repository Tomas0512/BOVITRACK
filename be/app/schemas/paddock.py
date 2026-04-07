"""
Módulo: schemas/paddock.py
¿Qué? Schemas Pydantic para validar datos de potreros.
¿Para qué? Gestionar el registro y rotación de potreros dentro de la finca,
           controlando área, capacidad y estado de cobertura.
¿Impacto? La rotación de potreros es crítica para la sostenibilidad ganadera.
          Sin validaciones, se podrían crear potreros con área 0 o capacidad negativa.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class PaddockCreate(BaseModel):
    """¿Qué? Datos requeridos para crear un potrero.
    ¿Para qué? Registrar un nuevo potrero con área en hectáreas y capacidad máxima.
    ¿Impacto? name, area_hectares y max_capacity son obligatorios y validados.
    """

    name: str
    area_hectares: Decimal
    max_capacity: int
    coverage_status: str = "bueno"
    pasture_type: str | None = None
    status: str = "libre"
    rest_start_date: date | None = None
    rest_end_date: date | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """¿Qué? Valida que el nombre del potrero tenga al menos 2 caracteres.
        ¿Para qué? Evitar nombres vacíos o sin sentido.
        ¿Impacto? El nombre es parte de la UniqueConstraint con farm_id.
        """
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v

    @field_validator("area_hectares")
    @classmethod
    def validate_area(cls, v: Decimal) -> Decimal:
        """¿Qué? Valida que el área sea un valor positivo.
        ¿Para qué? Un potrero con 0 hectáreas no tiene sentido operativo.
        ¿Impacto? Dato utilizado en reportes de densidad animal por hectárea.
        """
        if v <= 0:
            raise ValueError("El área debe ser mayor a 0")
        return v

    @field_validator("max_capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        """¿Qué? Valida que la capacidad máxima sea positiva.
        ¿Para qué? Controlar cuántos animales puede sostener el potrero.
        ¿Impacto? Previene sobrepastoreo y degradación del suelo.
        """
        if v <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return v


class PaddockUpdate(BaseModel):
    """¿Qué? Schema para actualización parcial de un potrero.
    ¿Para qué? Actualizar estado (libre/ocupado/en_descanso), cobertura, o fechas de descanso.
    ¿Impacto? Permite gestionar la rotación sin recrear el potrero.
    """

    name: str | None = None
    area_hectares: Decimal | None = None
    max_capacity: int | None = None
    coverage_status: str | None = None
    pasture_type: str | None = None
    status: str | None = None
    rest_start_date: date | None = None
    rest_end_date: date | None = None


class PaddockResponse(BaseModel):
    """¿Qué? Schema de respuesta para un potrero.
    ¿Para qué? Definir la estructura JSON que retorna la API.
    ¿Impacto? Incluye rest_start_date y rest_end_date para gestión de rotación.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    area_hectares: Decimal
    max_capacity: int
    coverage_status: str
    pasture_type: str | None
    status: str
    rest_start_date: date | None
    rest_end_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
