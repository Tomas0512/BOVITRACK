"""
Módulo: schemas/audit.py
HU015 - Revisión de auditorías del sistema (Sprint 8 - Camilo)

COMO: Administrador del sistema
QUIERO: contar con contratos de datos claros para consultar la auditoría
        (filtros de entrada y estructura de salida)
PARA:   que el frontend reciba siempre la misma forma de respuesta, con los
        datos del usuario resueltos y con la información de paginación, sin
        depender de la estructura interna de la tabla `audit_log`.

¿Qué?     Schemas Pydantic de entrada (filtros) y salida (registros + página).
¿Para qué? Validar los parámetros de búsqueda y serializar la respuesta.
¿Impacto? Si un filtro llega mal formado, FastAPI responde 422 con el detalle
          en lugar de ejecutar una consulta inválida contra la base de datos.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuditExportFormat(str, Enum):
    """¿Qué? Formatos disponibles para entregar la auditoría.

    COMO: Administrador
    QUIERO: elegir entre ver los datos en pantalla o descargarlos
    PARA:   poder archivar o enviar la evidencia de auditoría fuera del sistema.
    """

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class AuditLogFilters(BaseModel):
    """¿Qué? Conjunto de filtros aceptados por la consulta de auditoría.

    COMO: Administrador que investiga un evento puntual
    QUIERO: acotar los registros por usuario, acción, entidad, finca y fechas
    PARA:   encontrar rápidamente quién hizo qué y cuándo, sin recorrer
            manualmente miles de registros.

    ¿Impacto? Todos los campos son opcionales: sin filtros se devuelve la
              auditoría completa de las fincas a las que el usuario tiene
              acceso, ordenada de la más reciente a la más antigua.
    """

    user_id: uuid.UUID | None = Field(
        default=None,
        description="Filtra por el usuario que ejecutó la acción",
    )
    farm_id: uuid.UUID | None = Field(
        default=None,
        description="Filtra por finca; si se omite, abarca todas las fincas accesibles",
    )
    action: str | None = Field(
        default=None,
        max_length=100,
        description="Coincidencia parcial e insensible a mayúsculas (ej: 'create')",
    )
    entity: str | None = Field(
        default=None,
        max_length=100,
        description="Coincidencia parcial e insensible a mayúsculas (ej: 'bovine')",
    )
    start_date: date | None = Field(
        default=None,
        description="Fecha inicial inclusive (YYYY-MM-DD)",
    )
    end_date: date | None = Field(
        default=None,
        description="Fecha final inclusive (YYYY-MM-DD)",
    )
    include_auth_events: bool = Field(
        default=True,
        description="Incluir eventos de sesión (login, logout, register, etc.)",
    )

    @model_validator(mode="after")
    def _validate_date_range(self) -> AuditLogFilters:
        """¿Qué? Verifica que el rango de fechas sea coherente.
        ¿Para qué? Evitar consultas que nunca devolverán resultados.
        ¿Impacto? Responde 422 en lugar de una lista vacía silenciosa.
        """
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date no puede ser posterior a end_date")
        return self


class AuditLogRecord(BaseModel):
    """¿Qué? Un registro de auditoría con los datos del usuario ya resueltos.

    COMO: Administrador
    QUIERO: ver el nombre y correo del responsable junto a la acción
    PARA:   identificar a la persona sin tener que cruzar manualmente el
            user_id contra la tabla de usuarios.
    """

    id: uuid.UUID
    user_id: uuid.UUID | None
    farm_id: uuid.UUID | None
    action: str
    entity: str
    entity_id: str | None
    details: str | None
    created_at: datetime
    user_email: str | None = None
    user_full_name: str | None = None
    farm_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogPage(BaseModel):
    """¿Qué? Página de resultados con su metadata de paginación.

    COMO: Administrador consultando un histórico extenso
    QUIERO: recibir los registros por páginas junto al total disponible
    PARA:   que la tabla del frontend cargue rápido y pueda mostrar
            "mostrando X de Y registros" sin traer todo a memoria.
    """

    total: int = Field(description="Cantidad total de registros que cumplen los filtros")
    limit: int = Field(description="Tamaño de página solicitado")
    offset: int = Field(description="Registros omitidos desde el inicio")
    items: list[AuditLogRecord] = Field(default_factory=list)
