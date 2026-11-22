"""
Módulo: shared/ports.py
Descripción: Interfaces (puertos) que varios módulos necesitan de otros dominios.

¿Qué? Contratos mínimos, escritos como `Protocol`, de lo que un módulo pide
      a otro: "deja constancia en la auditoría" o "valida que esto sea de la finca".
¿Para qué? Que un servicio dependa de *qué* necesita y no de *quién* lo hace.
           Cada módulo conecta la implementación real en su `dependencies.py`,
           y en las pruebas se pasa una función falsa sin base de datos.
¿Impacto? Viven en shared porque los comparten varios módulos. Si quedaran en el
          primer módulo que las necesitó, los demás tendrían que importar sus
          internos, y eso rompe la frontera (lo verifica import-linter).
"""

import uuid
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Protocol


class CurrentUser(Protocol):
    """Lo único que los módulos necesitan saber del usuario autenticado: su id.

    ¿Por qué no el modelo ORM User? Porque los routers de los módulos solo usan
    current_user.id. Así no se acoplan a la tabla de usuarios de identity.
    """

    @property
    def id(self) -> uuid.UUID: ...


@dataclass(frozen=True)
class BovineRef:
    """Lo mínimo que otro módulo necesita saber de un bovino.

    ¿Por qué no el modelo ORM Bovine? Porque así el módulo que pregunta no se
    acopla a la tabla de ganado: solo recibe estos dos datos de solo lectura.
    """

    id: uuid.UUID
    sex: str


class BovineLookup(Protocol):
    """Busca un bovino *dentro de la finca*. None si no existe o es de otra finca."""

    def __call__(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> BovineRef | None: ...


@dataclass(frozen=True)
class PaddockRef:
    """Lo mínimo que otro módulo necesita saber de un potrero: a qué lote pertenece."""

    id: uuid.UUID
    land_plot_id: uuid.UUID | None


class PaddockLookup(Protocol):
    """Busca un potrero ACTIVO dentro de la finca. None si no existe, está inactivo o es de otra finca."""

    def __call__(self, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> PaddockRef | None: ...


class LandPlotLookup(Protocol):
    """¿El lote existe y pertenece a la finca?"""

    def __call__(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> bool: ...


class AuditRecorder(Protocol):
    """Deja constancia de una acción en la auditoría de negocio."""

    def __call__(
        self,
        *,
        user_id: str | None,
        action: str,
        entity: str,
        entity_id: str | None = None,
        farm_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...


class FarmScopeChecker(Protocol):
    """Valida que bovino, lote y responsable pertenezcan a la finca.

    Si algo no pertenece, lanza BusinessRuleError (400) y la operación no
    continúa. Implementación: farms.build_farm_scope_checker.
    """

    def __call__(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        land_plot_id: uuid.UUID | None = None,
        member_user_id: uuid.UUID | None = None,
    ) -> None: ...


# ── Datos que alimentan las alertas (los provee salud e inventario) ─────────


@dataclass(frozen=True)
class SanitaryDue:
    """Un plan sanitario con fecha de aplicación, visto desde fuera del dominio de salud."""

    id: uuid.UUID
    vaccine_or_treatment_name: str
    treatment_type: str
    next_scheduled_date: date | None
    bovine_id: uuid.UUID | None
    land_plot_id: uuid.UUID | None


@dataclass(frozen=True)
class LowStockItem:
    """Un insumo cuyo stock está en o por debajo de su mínimo, visto desde fuera de inventario."""

    id: uuid.UUID
    name: str
    category: str
    current_stock: Decimal
    min_stock_alert: Decimal | None
    unit_of_measure: str


class SanitaryAlertsSource(Protocol):
    """Planes sanitarios activos vencidos o próximos de una finca."""

    def overdue(self, farm_id: uuid.UUID, now: datetime) -> list[SanitaryDue]: ...

    def upcoming(self, farm_id: uuid.UUID, now: datetime, until: datetime) -> list[SanitaryDue]: ...


class LowStockLookup(Protocol):
    """Insumos activos en stock bajo, del menor stock al mayor."""

    def __call__(self, farm_id: uuid.UUID) -> list[LowStockItem]: ...


# ── Personas y correo (los provee identidad y core) ─────────────────────────


class FarmMemberLookup(Protocol):
    """IDs de los usuarios con membresía activa en la finca."""

    def __call__(self, farm_id: uuid.UUID) -> list[uuid.UUID]: ...


class FarmMembershipCheck(Protocol):
    """¿El usuario tiene una membresía ACTIVA en la finca? Implementación: identity."""

    def __call__(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...


class UserEmailLookup(Protocol):
    """Correo del usuario, o None si no existe o no tiene."""

    def __call__(self, user_id: uuid.UUID) -> str | None: ...


class EmailSender(Protocol):
    """Envía un correo (asíncrono). Implementación: app.core.email.send_generic_email."""

    def __call__(self, *, to_email: str, subject: str, body_html: str, label: str) -> Awaitable[None]: ...
