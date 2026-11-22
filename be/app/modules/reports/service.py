"""
Módulo: modules/reports/service.py
¿Qué? Casos de uso de reportes: estadísticas de la finca, leche diaria,
      resúmenes de todas las fincas del usuario y el reporte filtrado
      (productivo, sanitario, económico), exportable a Excel o PDF.
¿Para qué? Dar al ganadero una foto consolidada de su operación.
¿Impacto? Garantiza que:
          - los resúmenes globales solo incluyen fincas del usuario (dueño o miembro);
          - el rango de fechas tiene sentido (no invertido, no futuro) -> 422;
          - un nombre de vista fuera de la lista blanca se rechaza ANTES de
            consultar la BD (protección contra inyección SQL).
          No conoce HTTP ni SQL: los números los trae el repositorio.
"""

import json
import uuid
from collections.abc import Callable
from datetime import date
from typing import Any

from app.modules.reports import exporters
from app.modules.reports.repository import ReportRepository, ensure_view_allowed
from app.modules.reports.schemas import (
    EconomicReport,
    ProductiveReport,
    ReportCategory,
    ReportFilterParams,
    ReportResponse,
    SanitaryReport,
)
from app.shared.exceptions import InvalidRequestError, NotFoundError

FARM_NOT_FOUND = "Farm not found"
START_AFTER_END = "La fecha inicial no puede ser posterior a la final"
START_IN_FUTURE = "La fecha inicial no puede ser futura"
END_IN_FUTURE = "La fecha final no puede ser futura"


class ReportService:
    """Casos de uso del módulo de reportes (solo lectura)."""

    def __init__(self, repository: ReportRepository, today: Callable[[], date] = date.today) -> None:
        self._repo = repository
        self._today = today

    # ── Consultas directas ───────────────────────────────────

    def farm_statistics(self, farm_id: uuid.UUID) -> Any:
        """JSON de fn_farm_statistics, o un mensaje si la finca no tiene estadísticas."""
        row = self._repo.farm_statistics(farm_id)
        if row is None:
            return {"message": "Farm without statistics"}
        return row

    def milk_daily(self, farm_id: uuid.UUID) -> list[dict[str, Any]]:
        return self._repo.milk_daily(farm_id)

    def view_for_user(self, user_id: uuid.UUID, view: str) -> list[dict[str, Any]]:
        """Filas de una vista global, acotadas a las fincas del usuario.

        La lista blanca se valida primero: un nombre malicioso nunca llega a la BD.
        """
        ensure_view_allowed(view)
        farm_ids = self._repo.accessible_farm_ids(user_id)
        if not farm_ids:
            return []
        return self._repo.view_rows(view, farm_ids)

    # ── Reporte filtrado ─────────────────────────────────────

    def validate_date_range(self, start_date: date | None, end_date: date | None) -> None:
        if start_date and end_date and start_date > end_date:
            raise InvalidRequestError(START_AFTER_END)
        today = self._today()
        if start_date and start_date > today:
            raise InvalidRequestError(START_IN_FUTURE)
        if end_date and end_date > today:
            raise InvalidRequestError(END_IN_FUTURE)

    def generate_report(self, farm_id: uuid.UUID, params: ReportFilterParams) -> ReportResponse:
        """Arma el reporte de las categorías pedidas (todas si no se indica ninguna)."""
        self.validate_date_range(params.start_date, params.end_date)
        farm_name = self._repo.farm_name(farm_id)
        if not farm_name:
            raise NotFoundError(FARM_NOT_FOUND)

        category = params.category
        report = ReportResponse(
            farm_id=farm_id,
            farm_name=farm_name,
            category=category,
            start_date=params.start_date,
            end_date=params.end_date,
        )
        if category is None or category == ReportCategory.PRODUCTIVE:
            report.productive = self.build_productive_report(farm_id, params.start_date, params.end_date)
        if category is None or category == ReportCategory.SANITARY:
            report.sanitary = self.build_sanitary_report(farm_id, params.start_date, params.end_date)
        if category is None or category == ReportCategory.ECONOMIC:
            report.economic = self.build_economic_report(farm_id, params.start_date, params.end_date)
        return report

    def build_productive_report(
        self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None
    ) -> ProductiveReport:
        stats: Any = self._repo.farm_statistics(farm_id)
        total_bovines = males = females = 0
        avg_weight = None
        if stats:
            if isinstance(stats, str):
                stats = json.loads(stats)
            if not isinstance(stats, dict):
                stats = {}
            total_bovines = stats.get("total_bovines", 0)
            males = stats.get("males", 0)
            females = stats.get("females", 0)
            avg_weight = stats.get("avg_weight")

        total_milk = self._repo.total_milk_liters(farm_id, start_date, end_date)
        # Promedio diario: días del rango pedido, o días reales con ordeño si no hay rango.
        avg_milk_per_day = 0.0
        if total_milk:
            days = (end_date - start_date).days + 1 if start_date and end_date else self._repo.milking_days(farm_id)
            if days > 0:
                avg_milk_per_day = round(float(total_milk) / days, 2)

        calves_by_age = self._repo.calves_by_age_group(farm_id)
        return ProductiveReport(
            total_bovines=total_bovines,
            males=males,
            females=females,
            avg_weight=avg_weight,
            total_milk_liters=float(total_milk),
            avg_milk_per_day=avg_milk_per_day,
            total_calves=sum(calves_by_age.values()),
            calves_by_age_group=calves_by_age,
        )

    def build_sanitary_report(
        self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None
    ) -> SanitaryReport:
        by_type = self._repo.treatments_by_type(farm_id, start_date, end_date)
        return SanitaryReport(
            total_treatments=sum(by_type.values()),
            active_sanitary_plans=self._repo.active_sanitary_plans(farm_id),
            # Dosis que faltan por aplicar: próxima aplicación desde hoy en adelante.
            # (Antes siempre era 0 porque nunca se calculaba.)
            pending_treatments=self._repo.pending_treatments(farm_id, self._today()),
            treatments_by_type=by_type,
        )

    def build_economic_report(
        self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None
    ) -> EconomicReport:
        total_income = 0.0
        total_expense = 0.0
        income_by_activity: dict[str, float] = {}
        expense_by_activity: dict[str, float] = {}
        for row in self._repo.economic_rows(farm_id, start_date, end_date):
            amount = float(row[0] or 0) if row[0] else 0.0
            expense = float(row[1] or 0) if row[1] else 0.0
            total_income += amount
            total_expense += expense
            activity = row[2]
            if amount > 0:
                income_by_activity[activity] = income_by_activity.get(activity, 0) + amount
            if expense > 0:
                expense_by_activity[activity] = expense_by_activity.get(activity, 0) + expense
        return EconomicReport(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            income_by_activity=income_by_activity,
            expense_by_activity=expense_by_activity,
        )

    # ── Exportación ──────────────────────────────────────────

    @staticmethod
    def export_to_excel(report: ReportResponse) -> bytes:
        return exporters.export_to_excel(report)

    @staticmethod
    def export_to_pdf(report: ReportResponse) -> bytes:
        return exporters.export_to_pdf(report)
