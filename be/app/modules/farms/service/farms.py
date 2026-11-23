"""
Módulo: modules/farms/service/farms.py (casos de uso de fincas y catálogos)
¿Qué? Crear (una o varias), listar, consultar, actualizar y desactivar fincas, y
      leer los catálogos del formulario (departamentos, ciudades, propósitos).
¿Para qué? Reglas de la finca sin HTTP ni SQL: identificador único, nombre único
           por municipio, quién la ve, y que su creador quede como Administrador.
¿Impacto? La membresía la crea identity (puerto MembershipGranter): farms no
          escribe en `user_farm`, pide que se escriba.
"""

import logging
import uuid
from typing import Any, Protocol

from app.modules.farms.models import City, Department, Farm, Purpose
from app.modules.farms.schemas import FarmBulkCreateResult, FarmBulkError, FarmCreate, FarmResponse, FarmUpdate
from app.shared.exceptions import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.shared.ports import AuditRecorder, FarmMembershipCheck

FARM_IDENTIFIER_TAKEN = "Ya existe una finca con ese identificador"
FARM_NAME_TAKEN = "Ya existe una finca con ese nombre en ese municipio"
FARM_NOT_FOUND = "Finca no encontrada"
UNEXPECTED_ROW_ERROR = "Error inesperado al crear esta finca; no se guardó."
NO_FARM_ACCESS = "No tienes acceso a esta finca"

logger = logging.getLogger(__name__)


class MembershipGranter(Protocol):
    """Puerto hacia identity: hace al usuario Administrador de la finca (sin commit)."""

    def __call__(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> None: ...


class MemberFarmIds(Protocol):
    """Puerto hacia identity: fincas donde el usuario tiene membresía activa."""

    def __call__(self, user_id: uuid.UUID) -> list[uuid.UUID]: ...


class FarmStore(Protocol):
    def get_active(self, farm_id: uuid.UUID) -> Farm | None: ...
    def by_identifier(self, identifier: str, *, exclude_id: uuid.UUID | None = None) -> Farm | None: ...
    def by_location(self, name: str, department_id: uuid.UUID, city: str, *, exclude_id: uuid.UUID | None = None) -> Farm | None: ...
    def list_visible(self, user_id: uuid.UUID, member_farm_ids: Any) -> list[Farm]: ...
    def add(self, farm: Farm) -> None: ...
    def flush(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def refresh(self, farm: Farm) -> None: ...


class FarmService:
    def __init__(
        self,
        repository: FarmStore,
        *,
        grant_admin: MembershipGranter,
        member_farm_ids: MemberFarmIds,
        is_member: FarmMembershipCheck,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._grant_admin = grant_admin
        self._member_farm_ids = member_farm_ids
        self._is_member = is_member
        self._record_audit = record_audit

    def create(self, data: FarmCreate, owner_id: uuid.UUID) -> Farm:
        """Crea la finca y deja a su creador como Administrador, en UNA transacción."""
        if self._repo.by_identifier(data.farm_identifier):
            raise ConflictError(FARM_IDENTIFIER_TAKEN)
        if self._repo.by_location(data.name, data.department_id, data.city_municipality):
            raise ConflictError(FARM_NAME_TAKEN)

        farm = Farm(owner_id=owner_id, **data.model_dump())
        self._repo.add(farm)
        self._repo.flush()  # asigna farm.id sin confirmar todavía
        self._grant_admin(owner_id, farm.id)
        self._audit(owner_id, farm, "create")
        self._repo.commit()
        self._repo.refresh(farm)
        return farm

    def create_many(self, items: list[FarmCreate], owner_id: uuid.UUID) -> FarmBulkCreateResult:
        """Carga masiva con reporte por fila: una finca que falla no detiene a las demás.

        Cada finca es su propia transacción (create confirma la suya). Las que ya
        entraron cuentan para validar las siguientes, así que un identificador
        repetido DENTRO de la misma lista también se reporta como error.
        """
        created: list[FarmResponse] = []
        errors: list[FarmBulkError] = []
        for row, item in enumerate(items, start=1):
            try:
                created.append(FarmResponse.model_validate(self.create(item, owner_id)))
            except DomainError as exc:  # regla de negocio: nada se escribió
                errors.append(FarmBulkError(row=row, farm_identifier=item.farm_identifier, error=exc.message))
            except Exception:  # noqa: BLE001 — falla inesperada: se deshace solo esta finca
                self._repo.rollback()
                logger.exception("Carga masiva de fincas: error inesperado en la fila %s", row)
                errors.append(FarmBulkError(row=row, farm_identifier=item.farm_identifier, error=UNEXPECTED_ROW_ERROR))
        return FarmBulkCreateResult(total=len(items), created=len(created), failed=len(errors), items=created, errors=errors)

    def list_for_user(self, user_id: uuid.UUID) -> list[Farm]:
        """Fincas activas donde es dueño o miembro activo."""
        return self._repo.list_visible(user_id, self._member_farm_ids(user_id))

    def get_for_user(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> Farm:
        farm = self._repo.get_active(farm_id)
        if not farm:
            raise NotFoundError(FARM_NOT_FOUND)
        if farm.owner_id != user_id and not self._is_member(farm_id, user_id):
            raise PermissionDeniedError(NO_FARM_ACCESS)
        return farm

    def update(self, farm_id: uuid.UUID, user_id: uuid.UUID, data: FarmUpdate) -> Farm:
        """Actualiza solo los campos enviados."""
        farm = self.get_for_user(farm_id, user_id)
        if data.farm_identifier and self._repo.by_identifier(data.farm_identifier, exclude_id=farm_id):
            raise ConflictError(FARM_IDENTIFIER_TAKEN)
        changes = data.model_dump(exclude_unset=True)
        name = changes.get("name", farm.name)
        department_id = changes.get("department_id", farm.department_id)
        city = changes.get("city_municipality", farm.city_municipality)
        if {"name", "department_id", "city_municipality"} & changes.keys() and self._repo.by_location(
            name, department_id, city, exclude_id=farm_id
        ):
            raise ConflictError(FARM_NAME_TAKEN)

        for field, value in changes.items():
            setattr(farm, field, value)
        self._audit(user_id, farm, "update")
        self._repo.commit()
        self._repo.refresh(farm)
        return farm

    def deactivate(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Soft delete: la finca deja de listarse, pero sus registros se conservan."""
        farm = self.get_for_user(farm_id, user_id)
        farm.is_active = False
        self._audit(user_id, farm, "delete")
        self._repo.commit()

    def _audit(self, user_id: uuid.UUID, farm: Farm, action: str) -> None:
        self._record_audit(user_id=str(user_id), farm_id=str(farm.id), action=action, entity="farm",
                           entity_id=str(farm.id), details={"name": farm.name})


class CatalogStore(Protocol):
    def departments(self) -> list[Department]: ...
    def cities(self, department_id: uuid.UUID) -> list[City]: ...
    def purposes(self) -> list[Purpose]: ...


class CatalogService:
    """Catálogos de solo lectura para el formulario de finca."""

    def __init__(self, repository: CatalogStore) -> None:
        self._repo = repository

    def departments(self) -> list[Department]:
        return self._repo.departments()

    def cities(self, department_id: uuid.UUID) -> list[City]:
        return self._repo.cities(department_id)

    def purposes(self) -> list[Purpose]:
        return self._repo.purposes()
