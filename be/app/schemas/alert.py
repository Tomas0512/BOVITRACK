"""
Módulo: schemas/alert.py
HU014 - Alertas y notificaciones (Sprint 8 - Tomas)

¿Qué? Schemas Pydantic de entrada y salida para las preferencias de
      notificación y el historial de notificaciones.
¿Para qué? Validar lo que envía el frontend y controlar la estructura JSON
           que devuelve la API.
¿Impacto? Si un campo llega inválido, FastAPI responde 422 con el detalle en
          lugar de guardar datos corruptos.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationPrefUpdate(BaseModel):
    """¿Qué? Campos que el usuario puede cambiar en sus preferencias.

    ¿Para qué? Permitir actualizar canal y qué tipos de eventos quiere recibir.
    ¿Impacto? Todos opcionales: solo se actualizan los enviados. Un booleano a
              `false` es válido y NO se confunde con "no enviado" (default None).
    """

    channel: str | None = Field(
        default=None,
        description="Canal de entrega: email | in_app | ambos",
    )
    frequency: str | None = Field(
        default=None,
        description="Frecuencia de entrega: real_time | daily | weekly",
    )
    notify_sanitary: bool | None = Field(
        default=None, description="Notificar planes sanitarios"
    )
    notify_low_stock: bool | None = Field(
        default=None, description="Notificar stock bajo de insumos"
    )
    notify_reproductive: bool | None = Field(
        default=None, description="Notificar eventos reproductivos"
    )
    notify_birth: bool | None = Field(
        default=None, description="Notificar nacimientos"
    )


class NotificationPrefResponse(BaseModel):
    """¿Qué? Preferencia de notificación serializada (respuesta).

    ¿Para qué? Que el frontend cargue el estado actual y lo muestre en el form.
    ¿Impacto? Incluye los campos normativos y los flags por tipo.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    channel: str
    frequency: str
    notify_sanitary: bool
    notify_low_stock: bool
    notify_reproductive: bool
    notify_birth: bool
    created_at: datetime
    updated_at: datetime


class NotificationLogResponse(BaseModel):
    """¿Qué? Notificación del historial serializada (respuesta).

    ¿Para qué? Mostrar en la web el historial de notificaciones.
    ¿Impacto? read_at nulo significa "no leída"; channel indica cómo se entregó.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    user_id: uuid.UUID | None
    type: str
    title: str
    message: str | None
    channel: str
    status: str
    reference_id: str | None
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime


class NotificationHistoryResponse(BaseModel):
    """¿Qué? Página de historial con metadatos de paginación.

    ¿Para qué? Que el frontend sepa cuántas hay y si hay más páginas.
    ¿Impacto? item_count equivale a los elementos de esta página.
    """

    items: list[NotificationLogResponse]
    total: int
    limit: int
    offset: int
