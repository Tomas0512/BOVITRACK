"""
Módulo: schemas/bovine.py
¿Qué? Schemas Pydantic para validar entrada y salida de datos de bovinos.
¿Para qué? Garantizar que los datos enviados al API cumplan con los tipos y
           restricciones esperados antes de llegar a la base de datos.
¿Impacto? Sin estos schemas, datos inválidos (ej: sexo="xyz", peso negativo)
          podrían insertarse directamente en la BD, causando inconsistencias.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class BovineCreate(BaseModel):
    """Schema para registrar un nuevo bovino en la finca.

    ¿Qué? Valida los campos obligatorios y opcionales al crear un bovino.
    ¿Para qué? Asegurar que identification_number, sex y entry_type son válidos.
    ¿Impacto? Rechaza peticiones malformadas con mensajes claros en español.
    """

    name: str | None = None
    identification_number: str
    sex: str
    breed: str | None = None
    color: str | None = None
    markings: str | None = None
    birth_date: date
    birth_weight: Decimal | None = None
    current_weight: Decimal | None = None
    father_id: uuid.UUID | None = None
    mother_id: uuid.UUID | None = None
    purpose: str | None = None
    status: str = "activo"
    entry_type: str
    entry_date: date
    land_plot_id: uuid.UUID | None = None
    observations: str | None = None

    @field_validator("identification_number")
    @classmethod
    def validate_identification(cls, v: str) -> str:
        """¿Qué? Valida que el número de identificación no esté vacío.
        ¿Para qué? Cada bovino DEBE tener un identificador único dentro de la finca.
        ¿Impacto? Sin esta validación, se podrían crear bovinos sin identificación.
        """
        v = v.strip()
        if len(v) < 1:
            raise ValueError("El número de identificación es obligatorio")
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str) -> str:
        """¿Qué? Restringe el sexo a 'macho' o 'hembra'.
        ¿Para qué? Evitar valores arbitrarios que dificultarían filtros y reportes.
        ¿Impacto? Normaliza a minúsculas para consistencia en la BD.
        """
        allowed = {"macho", "hembra"}
        if v.lower() not in allowed:
            raise ValueError("El sexo debe ser 'macho' o 'hembra'")
        return v.lower()

    @field_validator("entry_type")
    @classmethod
    def validate_entry_type(cls, v: str) -> str:
        """¿Qué? Valida el tipo de ingreso del bovino a la finca.
        ¿Para qué? Controlar cómo llegó el animal: nacimiento, compra, donación o traspaso.
        ¿Impacto? Dato clave para trazabilidad y auditoría del hato ganadero.
        """
        allowed = {"nacimiento", "compra", "donacion", "traspaso"}
        if v.lower() not in allowed:
            raise ValueError(f"Tipo de entrada inválido. Opciones: {', '.join(allowed)}")
        return v.lower()


class BovineUpdate(BaseModel):
    """Schema para actualización parcial de un bovino.

    ¿Qué? Todos los campos son opcionales — solo se actualizan los enviados.
    ¿Para qué? Permitir actualizar peso, estado, potrero, etc. sin reenviar todo.
    ¿Impacto? Usa exclude_unset=True en el service para no sobreescribir con None.
    """

    name: str | None = None
    identification_number: str | None = None
    sex: str | None = None
    breed: str | None = None
    color: str | None = None
    markings: str | None = None
    birth_date: date | None = None
    birth_weight: Decimal | None = None
    current_weight: Decimal | None = None
    father_id: uuid.UUID | None = None
    mother_id: uuid.UUID | None = None
    purpose: str | None = None
    status: str | None = None
    land_plot_id: uuid.UUID | None = None
    exit_date: date | None = None
    exit_reason: str | None = None
    observations: str | None = None


class BovineResponse(BaseModel):
    """Schema de respuesta que serializa un bovino desde la BD.

    ¿Qué? Define exactamente qué campos retorna la API al frontend.
    ¿Para qué? Controlar la forma del JSON de respuesta y evitar exponer datos internos.
    ¿Impacto? from_attributes=True permite crear el schema directamente desde el modelo ORM.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    land_plot_id: uuid.UUID | None
    name: str | None
    identification_number: str
    sex: str
    breed: str | None
    color: str | None
    markings: str | None
    birth_date: date
    birth_weight: Decimal | None
    current_weight: Decimal | None
    father_id: uuid.UUID | None
    mother_id: uuid.UUID | None
    purpose: str | None
    status: str
    entry_type: str
    entry_date: date
    exit_date: date | None
    exit_reason: str | None
    observations: str | None
    is_active: bool
    registered_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
