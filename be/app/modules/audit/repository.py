"""
Módulo: modules/audit/repository.py (modelo de LECTURA)
¿Qué? Consultas sobre `audit_log`: filtros, paginación, catálogo de acciones,
      auditoría de una finca y fincas visibles para el usuario.
¿Para qué? Que el servicio pida "la página N de la auditoría con estos filtros"
           sin escribir consultas.
¿Impacto? Para mostrar nombres de usuario y finca cruza las tablas `users`,
          `farm` y `user_farm`. Las toma de Base.metadata (el esquema de la BD),
          SIN importar los modelos de identity ni de farms: como en reports, el
          acoplamiento es con el esquema y no con el código de otros módulos.
          La escritura de auditoría NO está aquí: es app.core.audit_trail.
"""

import uuid
from collections.abc import Sequence
from datetime import date, datetime, time
from typing import Any, Protocol

from sqlalchemy import Table, func, select
from sqlalchemy.orm import Session

from app.core.audit_trail import AuditLog
from app.core.database import Base

# Acciones del ciclo de sesión del usuario: el administrador puede excluirlas
# para ver solo los cambios sobre los datos del negocio.
AUTH_ACTIONS: frozenset[str] = frozenset({
    "login",
    "logout",
    "logout_all_sessions",
    "register",
    "email_verified",
    "password_reset",
})

class AuditFilterValues(Protocol):
    """Los filtros que el repositorio necesita (los cumple schemas.AuditFilterValues).

    Se declaran aquí, y no se importa el schema, porque el repositorio está en una
    capa inferior a los schemas: solo conoce la forma de los datos que recibe.
    """

    farm_id: uuid.UUID | None
    user_id: uuid.UUID | None
    action: str | None
    entity: str | None
    start_date: date | None
    end_date: date | None
    include_auth_events: bool


def _table(name: str) -> Table:
    """Tabla del esquema registrado (users, farm, user_farm)."""
    return Base.metadata.tables[name]


def _build_filter_conditions(
    filters: AuditFilterValues,
    accessible_farm_ids: list[uuid.UUID],
) -> list:
    """¿Qué? Traduce los filtros del schema a condiciones SQLAlchemy.

    COMO: desarrollador que mantiene el módulo
    QUIERO: construir las condiciones en un solo lugar
    PARA:   que el conteo total y la página de resultados usen exactamente los
            mismos criterios y nunca se desincronicen.

    ¿Impacto? El alcance por finca se aplica SIEMPRE, incluso si el usuario
              envía un farm_id al que no tiene acceso.
    """
    conditions: list = []

    # Alcance obligatorio: solo fincas del usuario.
    if filters.farm_id is not None:
        # Si pide una finca puntual, debe estar dentro de las accesibles.
        if filters.farm_id in accessible_farm_ids:
            conditions.append(AuditLog.farm_id == filters.farm_id)
        else:
            # Condición imposible → resultado vacío sin exponer si la finca existe.
            conditions.append(AuditLog.farm_id.is_(None))
            conditions.append(AuditLog.farm_id.is_not(None))
    else:
        conditions.append(AuditLog.farm_id.in_(accessible_farm_ids))

    if filters.user_id is not None:
        conditions.append(AuditLog.user_id == filters.user_id)

    # Coincidencia parcial e insensible a mayúsculas: buscar "creat" encuentra
    # "create_bovine" y "CREATE_FARM".
    if filters.action:
        conditions.append(AuditLog.action.ilike(f"%{filters.action}%"))

    if filters.entity:
        conditions.append(AuditLog.entity.ilike(f"%{filters.entity}%"))

    # Las fechas son inclusivas en ambos extremos: end_date 2026-08-18 incluye
    # todo lo ocurrido ese día hasta las 23:59:59.
    if filters.start_date:
        conditions.append(
            AuditLog.created_at >= datetime.combine(filters.start_date, time.min)
        )

    if filters.end_date:
        conditions.append(
            AuditLog.created_at <= datetime.combine(filters.end_date, time.max)
        )

    if not filters.include_auth_events:
        conditions.append(AuditLog.action.notin_(AUTH_ACTIONS))

    return conditions


class AuditRepository:
    """Consultas de solo lectura sobre la auditoría."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def accessible_farm_ids(self, user_id: str | uuid.UUID) -> list[uuid.UUID]:
        """Fincas donde el usuario es miembro activo (su auditoría es la única visible)."""
        user_farm = _table("user_farm")
        stmt = select(user_farm.c.farm_id).where(user_farm.c.user_id == user_id, user_farm.c.is_active.is_(True))
        return list(self._db.execute(stmt).scalars().all())

    def count(self, filters: AuditFilterValues, farm_ids: list[uuid.UUID]) -> int:
        conditions = _build_filter_conditions(filters, farm_ids)
        return self._db.execute(select(func.count()).select_from(AuditLog).where(*conditions)).scalar_one()

    def page(self, filters: AuditFilterValues, farm_ids: list[uuid.UUID], *, limit: int, offset: int) -> Sequence[Any]:
        """Filas (registro, correo, nombre, apellido, finca), del más reciente al más antiguo."""
        conditions = _build_filter_conditions(filters, farm_ids)
        users, farm = _table("users"), _table("farm")
        stmt = (
            select(AuditLog, users.c.email, users.c.first_name, users.c.last_name, farm.c.name)
            .outerjoin(users, users.c.id == AuditLog.user_id)
            .outerjoin(farm, farm.c.id == AuditLog.farm_id)
            .where(*conditions)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.execute(stmt).all()

    def _distinct(self, column: Any, farm_ids: list[uuid.UUID]) -> list[str]:
        stmt = select(column).where(AuditLog.farm_id.in_(farm_ids)).distinct().order_by(column)
        return list(self._db.execute(stmt).scalars().all())

    def distinct_actions(self, farm_ids: list[uuid.UUID]) -> list[str]:
        """Acciones distintas registradas en las fincas indicadas."""
        return self._distinct(AuditLog.action, farm_ids)

    def distinct_entities(self, farm_ids: list[uuid.UUID]) -> list[str]:
        """Entidades distintas registradas en las fincas indicadas."""
        return self._distinct(AuditLog.entity, farm_ids)

    def farm_logs(self, farm_id: uuid.UUID, *, limit: int = 500) -> Sequence[Any]:
        """Auditoría de datos de la finca (sin eventos de sesión), con correo y nombre del autor."""
        users = _table("users")
        stmt = (
            select(AuditLog, users.c.email, users.c.first_name, users.c.last_name)
            .outerjoin(users, users.c.id == AuditLog.user_id)
            .where(AuditLog.farm_id == farm_id, AuditLog.action.notin_(AUTH_ACTIONS))
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return self._db.execute(stmt).all()
