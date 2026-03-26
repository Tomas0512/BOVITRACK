"""
Módulo: schemas/treatment.py
¿Qué? Schemas Pydantic para validar datos de tratamientos sanitarios.
¿Para qué? Asegurar que cada tratamiento tenga tipo, producto, dosis y vía
           de administración antes de persistirse en la base de datos.
¿Impacto? Datos sanitarios mal registrados pueden afectar la salud del hato
          y generar problemas de trazabilidad ante el ICA.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TreatmentCreate(BaseModel):
    """¿Qué? Datos requeridos para registrar un tratamiento sanitario.
    ¿Para qué? Asociar un tratamiento a un bovino y/o potrero específico.
    ¿Impacto? treatment_type, product_name, dose y administration_route son obligatorios.
    """

    bovine_id: uuid.UUID | None = None
    land_plot_id: uuid.UUID | None = None
    treatment_type: str
    product_name: str
    dose: str
    administration_route: str
    application_date: datetime
    next_application_date: date | None = None
    diagnosis: str | None = None
    symptoms: str | None = None
    observations: str | None = None
    food_id: uuid.UUID | None = None


class TreatmentResponse(BaseModel):
    """¿Qué? Schema de respuesta para un tratamiento.
    ¿Para qué? Definir la estructura JSON que retorna la API al consultar tratamientos.
    ¿Impacto? Incluye applied_by para saber quién aplicó el tratamiento (auditoría).
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    bovine_id: uuid.UUID | None
    land_plot_id: uuid.UUID | None
    treatment_type: str
    product_name: str
    dose: str
    administration_route: str
    application_date: datetime
    next_application_date: date | None
    diagnosis: str | None
    symptoms: str | None
    observations: str | None
    food_id: uuid.UUID | None
    applied_by: uuid.UUID
    created_at: datetime
