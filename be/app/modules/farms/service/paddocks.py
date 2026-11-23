"""
Módulo: modules/farms/service/paddocks.py (casos de uso de potreros)
¿Qué? Registrar, listar, consultar, actualizar y desactivar potreros, y armar la
      respuesta con los animales que hay en cada uno.
¿Para qué? Reglas de la rotación: el potrero cuelga de un lote ACTIVO de la misma
           finca, no supera la capacidad ni el área del lote, su nombre es único
           en la finca y un lote nunca se queda sin potreros.
¿Impacto? Los animales se leen en una sola consulta para todos los potreros (sin N+1).
"""

from __future__ import annotations  # permite métodos llamados list sin tapar el tipo list

import uuid
from decimal import Decimal
from typing import Any, Protocol

from app.modules.farms.models import LandPlot, Paddock
from app.modules.farms.schemas import BovineRef, PaddockCreate, PaddockResponse, PaddockUpdate
from app.modules.farms.service.land_plots import paddock_name_taken
from app.shared.exceptions import BusinessRuleError, ConflictError, InvalidRequestError, NotFoundError
from app.shared.ports import AuditRecorder

PADDOCK_NOT_FOUND = "Potrero no encontrado"
LAND_PLOT_UNUSABLE = "El lote indicado no existe o no pertenece a esta finca."
LAST_PADDOCK = (
    "No se puede eliminar el único potrero del lote. "
    "Cree otro potrero primero o elimine el lote completo."
)


class PaddockStore(Protocol):
    def get_in_farm(self, farm_id: uuid.UUID, paddock_id: uuid.UUID, *, only_active: bool = False) -> Paddock | None: ...
    def list(self, farm_id: uuid.UUID, *, status: str | None = None, land_plot_id: uuid.UUID | None = None) -> list[Paddock]: ...
    def first_taken_name(self, farm_id: uuid.UUID, names: Any) -> str | None: ...
    def count_other_active_in_land_plot(self, land_plot_id: uuid.UUID, exclude_id: uuid.UUID) -> int: ...
    def animals_by_paddock(self, paddock_ids: Any) -> dict[uuid.UUID, list[dict]]: ...
    def add(self, paddock: Paddock) -> None: ...
    def flush(self) -> None: ...
    def commit(self) -> None: ...
    def refresh(self, paddock: Paddock) -> None: ...


class LandPlotReader(Protocol):
    def get_in_farm(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID, *, only_active: bool = False) -> LandPlot | None: ...


class PaddockService:
    def __init__(self, paddocks: PaddockStore, land_plots: LandPlotReader, *, record_audit: AuditRecorder) -> None:
        self._repo = paddocks
        self._land_plots = land_plots
        self._record_audit = record_audit

    def create(self, farm_id: uuid.UUID, data: PaddockCreate, user_id: uuid.UUID | None = None) -> Paddock:
        plot = self._usable_land_plot(farm_id, data.land_plot_id)
        self._check_limits(plot, data.max_capacity, data.area_hectares)
        if self._repo.first_taken_name(farm_id, [data.name]):
            raise ConflictError(paddock_name_taken(data.name))

        paddock = Paddock(farm_id=farm_id, **data.model_dump())
        self._repo.add(paddock)
        self._repo.flush()
        self._audit(user_id, farm_id, paddock, "create", {"name": paddock.name})
        self._repo.commit()
        self._repo.refresh(paddock)
        return paddock

    def list(self, farm_id: uuid.UUID, *, status: str | None = None, land_plot_id: uuid.UUID | None = None) -> list[Paddock]:
        return self._repo.list(farm_id, status=status, land_plot_id=land_plot_id)

    def get(self, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> Paddock:
        paddock = self._repo.get_in_farm(farm_id, paddock_id)
        if not paddock:
            raise NotFoundError(PADDOCK_NOT_FOUND)
        return paddock

    def update(self, farm_id: uuid.UUID, paddock_id: uuid.UUID, data: PaddockUpdate, user_id: uuid.UUID | None = None) -> Paddock:
        """Cambia estado, cobertura, fechas... Moverlo de lote es válido si el destino es de la finca."""
        paddock = self.get(farm_id, paddock_id)
        changes = data.model_dump(exclude_unset=True)
        plot = self._usable_land_plot(farm_id, changes.get("land_plot_id", paddock.land_plot_id))
        if "max_capacity" in changes or "area_hectares" in changes:
            self._check_limits(
                plot,
                changes.get("max_capacity", paddock.max_capacity),
                changes.get("area_hectares", paddock.area_hectares),
            )
        new_name = changes.get("name")
        if new_name and new_name != paddock.name and self._repo.first_taken_name(farm_id, [new_name]):
            raise ConflictError(paddock_name_taken(new_name))

        for field, value in changes.items():
            setattr(paddock, field, value)
        self._audit(user_id, farm_id, paddock, "update", {"name": paddock.name, "status": paddock.status})
        self._repo.commit()
        self._repo.refresh(paddock)
        return paddock

    def deactivate(self, farm_id: uuid.UUID, paddock_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Soft delete. Un lote no puede quedarse sin potreros activos."""
        paddock = self.get(farm_id, paddock_id)
        if self._repo.count_other_active_in_land_plot(paddock.land_plot_id, paddock_id) == 0:
            raise BusinessRuleError(LAST_PADDOCK)
        paddock.is_active = False
        self._audit(user_id, farm_id, paddock, "delete", {"name": paddock.name})
        self._repo.commit()

    def with_animals(self, paddocks: list[Paddock]) -> list[PaddockResponse]:
        """Respuestas con los bovinos activos de cada potrero (una sola consulta para todos)."""
        animals = self._repo.animals_by_paddock([p.id for p in paddocks])
        responses = []
        for paddock in paddocks:
            response = PaddockResponse.model_validate(paddock)
            response.animals = [BovineRef(**animal) for animal in animals.get(paddock.id, [])]
            response.animal_count = len(response.animals)
            responses.append(response)
        return responses

    # ── Reglas internas
    def _usable_land_plot(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> LandPlot:
        """El lote debe existir, estar activo y ser de ESTA finca (finca > lote > potrero)."""
        plot = self._land_plots.get_in_farm(farm_id, land_plot_id, only_active=True)
        if plot is None:
            raise InvalidRequestError(LAND_PLOT_UNUSABLE)
        return plot

    @staticmethod
    def _check_limits(plot: LandPlot, max_capacity: int | None, area_hectares: Decimal | None) -> None:
        """El potrero no puede superar la capacidad ni el área de su lote (evita sobrepastoreo)."""
        if max_capacity is not None and max_capacity > plot.max_capacity:
            raise InvalidRequestError(f"La capacidad del potrero no puede superar la del lote ({plot.max_capacity}).")
        if area_hectares is not None and area_hectares > plot.area:
            raise InvalidRequestError(f"El área del potrero no puede superar la del lote ({plot.area} {plot.area_unit}).")

    def _audit(self, user_id: uuid.UUID | None, farm_id: uuid.UUID, paddock: Paddock, action: str, details: dict) -> None:
        self._record_audit(user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action=action,
                           entity="paddock", entity_id=str(paddock.id), details=details)
