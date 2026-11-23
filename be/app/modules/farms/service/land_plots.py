"""
Módulo: modules/farms/service/land_plots.py (casos de uso de lotes)
¿Qué? Crear un lote junto con sus potreros, listarlos, consultarlos, actualizarlos
      y desactivarlos.
¿Para qué? Nombres únicos por finca (de lotes y de potreros) y un lote nunca
           queda creado a medias: lote y potreros van en la misma transacción.
¿Impacto? Desactivar un lote desactiva también sus potreros (soft delete).
"""

from __future__ import annotations  # permite métodos llamados list sin tapar el tipo list

import uuid
from typing import Any, Protocol

from app.modules.farms.models import LandPlot, Paddock
from app.modules.farms.schemas import LandPlotCreate, LandPlotUpdate
from app.shared.exceptions import ConflictError, NotFoundError
from app.shared.ports import AuditRecorder

LAND_PLOT_NAME_TAKEN = "Ya existe un lote con ese nombre en esta finca"
LAND_PLOT_NOT_FOUND = "Lote no encontrado"


def paddock_name_taken(name: str) -> str:
    return f"Ya existe un potrero llamado '{name}' en esta finca"


class LandPlotStore(Protocol):
    def get_in_farm(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID, *, only_active: bool = False) -> LandPlot | None: ...
    def by_name(self, farm_id: uuid.UUID, name: str, *, exclude_id: uuid.UUID | None = None) -> LandPlot | None: ...
    def list(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[LandPlot]: ...
    def add(self, land_plot: LandPlot) -> None: ...
    def flush(self) -> None: ...
    def commit(self) -> None: ...
    def refresh(self, land_plot: LandPlot) -> None: ...


class PaddockWriter(Protocol):
    def first_taken_name(self, farm_id: uuid.UUID, names: Any) -> str | None: ...
    def of_land_plot(self, land_plot_id: uuid.UUID) -> list[Paddock]: ...
    def add(self, paddock: Paddock) -> None: ...


class LandPlotService:
    def __init__(self, land_plots: LandPlotStore, paddocks: PaddockWriter, *, record_audit: AuditRecorder) -> None:
        self._repo = land_plots
        self._paddocks = paddocks
        self._record_audit = record_audit

    def create(self, farm_id: uuid.UUID, data: LandPlotCreate, user_id: uuid.UUID | None = None) -> LandPlot:
        if self._repo.by_name(farm_id, data.name):
            raise ConflictError(LAND_PLOT_NAME_TAKEN)

        payload = data.model_dump()
        paddocks = payload.pop("paddocks", [])
        names = [p["name"] for p in paddocks]
        # Se valida ANTES de escribir nada, para no dejar el lote a medias.
        taken = self._paddocks.first_taken_name(farm_id, names)
        if taken:
            raise ConflictError(paddock_name_taken(taken))

        land_plot = LandPlot(farm_id=farm_id, **payload)
        self._repo.add(land_plot)
        self._repo.flush()  # asigna land_plot.id sin confirmar todavía
        for paddock in paddocks:
            self._paddocks.add(Paddock(farm_id=farm_id, land_plot_id=land_plot.id, **paddock))
        self._audit(user_id, farm_id, land_plot, "create", {"name": land_plot.name, "paddocks": names})
        self._repo.commit()
        self._repo.refresh(land_plot)
        return land_plot

    def list(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[LandPlot]:
        return self._repo.list(farm_id, is_active=is_active)

    def get(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> LandPlot:
        land_plot = self._repo.get_in_farm(farm_id, land_plot_id)
        if not land_plot:
            raise NotFoundError(LAND_PLOT_NOT_FOUND)
        return land_plot

    def update(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID, data: LandPlotUpdate, user_id: uuid.UUID | None = None) -> LandPlot:
        land_plot = self.get(farm_id, land_plot_id)
        if data.name is not None and data.name != land_plot.name and self._repo.by_name(farm_id, data.name, exclude_id=land_plot_id):
            raise ConflictError(LAND_PLOT_NAME_TAKEN)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(land_plot, field, value)
        self._audit(user_id, farm_id, land_plot, "update", {"name": land_plot.name})
        self._repo.commit()
        self._repo.refresh(land_plot)
        return land_plot

    def deactivate(self, farm_id: uuid.UUID, land_plot_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Soft delete del lote y de TODOS sus potreros; el historial se conserva."""
        land_plot = self.get(farm_id, land_plot_id)
        land_plot.is_active = False
        for paddock in self._paddocks.of_land_plot(land_plot.id):
            paddock.is_active = False
        self._audit(user_id, farm_id, land_plot, "delete", {"name": land_plot.name})
        self._repo.commit()

    def _audit(self, user_id: uuid.UUID | None, farm_id: uuid.UUID, land_plot: LandPlot, action: str, details: dict) -> None:
        self._record_audit(user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action=action,
                           entity="land_plot", entity_id=str(land_plot.id), details=details)
