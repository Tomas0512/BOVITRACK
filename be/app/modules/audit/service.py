"""
Módulo: modules/audit/service.py
HU015 - Revisión de auditorías del sistema (Sprint 8 - Camilo)

¿Qué? Casos de uso de la CONSULTA de auditoría: listado filtrado y paginado,
      catálogo de acciones y entidades, exportación a CSV/Excel y auditoría
      de una finca.
¿Para qué? Rastrear quién modificó qué información y cuándo, y responder ante
           inconsistencias o reclamos sobre los datos de la finca.
¿Impacto? Garantiza que un usuario solo ve la auditoría de SUS fincas: pedir una
          finca ajena produce una condición imposible (cero registros), nunca un
          error que revele que existe. No conoce HTTP ni SQLAlchemy.
"""

import uuid

from app.modules.audit import exporters
from app.modules.audit.repository import AUTH_ACTIONS, AuditRepository
from app.modules.audit.schemas import (
    AuditExportFormat,
    AuditLogFilters,
    AuditLogPage,
    AuditLogRecord,
    AuditLogResponse,
)
from app.shared.exceptions import BusinessRuleError

EXPORT_MAX_ROWS = 10_000
JSON_EXPORT_NOT_ALLOWED = "Para consultar en JSON usa GET /api/v1/admin/audit-logs"

__all__ = ["AUTH_ACTIONS", "EXPORT_MAX_ROWS", "AuditService"]


def _full_name(first_name: str | None, last_name: str | None) -> str | None:
    return f"{first_name} {last_name}" if first_name is not None else None


class AuditService:
    """Casos de uso de la consulta de auditoría (solo lectura)."""

    def __init__(self, repository: AuditRepository) -> None:
        self._repo = repository

    def list_audit_logs(
        self,
        *,
        current_user_id: str | uuid.UUID,
        filters: AuditLogFilters,
        limit: int = 100,
        offset: int = 0,
    ) -> AuditLogPage:
        """Página de auditoría de las fincas del usuario, con el total para paginar."""
        accessible_farm_ids = self._repo.accessible_farm_ids(current_user_id)
        if not accessible_farm_ids:
            return AuditLogPage(total=0, limit=limit, offset=offset, items=[])
        items = [
            AuditLogRecord(
                id=log.id,
                user_id=log.user_id,
                farm_id=log.farm_id,
                action=log.action,
                entity=log.entity,
                entity_id=log.entity_id,
                details=log.details,
                created_at=log.created_at,
                user_email=email,
                user_full_name=_full_name(first_name, last_name),
                farm_name=farm_name,
            )
            for log, email, first_name, last_name, farm_name in self._repo.page(
                filters, accessible_farm_ids, limit=limit, offset=offset
            )
        ]
        total = self._repo.count(filters, accessible_farm_ids)
        return AuditLogPage(total=total, limit=limit, offset=offset, items=items)

    def catalog(self, current_user_id: str | uuid.UUID) -> dict[str, list[str]]:
        """Acciones y entidades existentes en las fincas del usuario (para los filtros)."""
        farm_ids = self._repo.accessible_farm_ids(current_user_id)
        if not farm_ids:
            return {"actions": [], "entities": []}
        return {
            "actions": self._repo.distinct_actions(farm_ids),
            "entities": self._repo.distinct_entities(farm_ids),
        }

    def collect_logs_for_export(
        self, *, current_user_id: str | uuid.UUID, filters: AuditLogFilters
    ) -> list[AuditLogRecord]:
        """Todos los registros que cumplen los filtros (hasta EXPORT_MAX_ROWS), sin paginar."""
        page = self.list_audit_logs(
            current_user_id=current_user_id, filters=filters, limit=EXPORT_MAX_ROWS, offset=0
        )
        return page.items

    def export(
        self, export_format: AuditExportFormat, *, current_user_id: str | uuid.UUID, filters: AuditLogFilters
    ) -> bytes:
        """Archivo CSV o Excel con la auditoría filtrada. JSON no se exporta (400)."""
        if export_format == AuditExportFormat.JSON:
            raise BusinessRuleError(JSON_EXPORT_NOT_ALLOWED)
        records = self.collect_logs_for_export(current_user_id=current_user_id, filters=filters)
        if export_format == AuditExportFormat.CSV:
            return exporters.export_to_csv(records)
        return exporters.export_to_excel(records)

    def farm_logs(self, farm_id: uuid.UUID) -> list[AuditLogResponse]:
        """Últimos 500 cambios de datos de la finca (sin eventos de sesión)."""
        return [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                entity=log.entity,
                entity_id=log.entity_id,
                details=log.details,
                created_at=log.created_at,
                user_email=email,
                user_full_name=_full_name(first_name, last_name),
            )
            for log, email, first_name, last_name in self._repo.farm_logs(farm_id)
        ]
