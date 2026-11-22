"""
Módulo: modules/reports/repository.py (modelo de LECTURA)
¿Qué? Todas las consultas SQL de los reportes: vistas (v_farm_summary,
      v_low_stock_alerts, v_pending_tasks, v_milk_production_daily), la función
      fn_farm_statistics y agregados sobre leche, crías, tratamientos, planes
      sanitarios y movimientos económicos.
¿Para qué? Concentrar en un solo lugar el SQL que cruza tablas de varios
           dominios. El servicio recibe números y filas, no consultas.
¿Impacto? Es la única excepción a "cada módulo consulta solo sus tablas": un
          reporte necesita leer de todos. Se acepta porque es SOLO lectura y el
          acoplamiento es con el esquema de la BD (vistas y columnas), no con el
          código Python de los otros módulos. Si cambia una columna, este es el
          único archivo de reportes que hay que revisar.
"""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.shared.exceptions import BusinessRuleError

# Vistas que se pueden consultar por nombre. El nombre se interpola en el SQL,
# así que NUNCA debe venir del usuario sin pasar por esta lista (inyección SQL).
ALLOWED_REPORT_VIEWS = frozenset({"v_farm_summary", "v_low_stock_alerts", "v_pending_tasks"})
VIEW_NOT_ALLOWED = "Vista de reporte no permitida"


def ensure_view_allowed(view: str) -> None:
    """Rechaza cualquier nombre de vista fuera de la lista blanca."""
    if view not in ALLOWED_REPORT_VIEWS:
        raise BusinessRuleError(VIEW_NOT_ALLOWED)


class ReportRepository:
    """Consultas de solo lectura para reportes, sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Fincas visibles para el usuario ──────────────────────

    def accessible_farm_ids(self, user_id: uuid.UUID) -> list[str]:
        """Fincas activas del usuario: las que posee y donde es miembro activo.

        Se consulta por SQL (tablas farm y user_farm) y no con los modelos ORM de
        fincas, para no acoplar este módulo al código Python de otro dominio.
        """
        params = {"user_id": str(user_id)}
        owned = self._db.execute(
            text("SELECT id FROM farm WHERE owner_id = :user_id AND is_active"), params
        ).scalars().all()
        member = self._db.execute(
            text("SELECT farm_id FROM user_farm WHERE user_id = :user_id AND is_active"), params
        ).scalars().all()
        return sorted({str(x) for x in owned} | {str(x) for x in member})

    def view_rows(self, view: str, farm_ids: list[str]) -> list[dict[str, Any]]:
        """Filas de una vista permitida, acotadas a las fincas indicadas."""
        ensure_view_allowed(view)
        result = self._db.execute(
            text(f"SELECT * FROM {view} WHERE farm_id IN :farm_ids").bindparams(
                bindparam("farm_ids", expanding=True)
            ),
            {"farm_ids": farm_ids},
        )
        return [dict(row._mapping) for row in result]

    # ── Estadísticas por finca ───────────────────────────────

    def farm_name(self, farm_id: uuid.UUID) -> str | None:
        return self._db.execute(text("SELECT name FROM farm WHERE id = :farm_id"), {"farm_id": str(farm_id)}).scalar_one_or_none()

    def farm_statistics(self, farm_id: uuid.UUID) -> Any:
        """Resultado crudo de fn_farm_statistics (JSON de Postgres) o None."""
        return self._db.execute(text("SELECT fn_farm_statistics(:farm_id)"), {"farm_id": str(farm_id)}).scalar_one_or_none()

    def milk_daily(self, farm_id: uuid.UUID) -> list[dict[str, Any]]:
        result = self._db.execute(
            text("SELECT * FROM v_milk_production_daily WHERE farm_id = :farm_id ORDER BY production_date DESC"),
            {"farm_id": str(farm_id)},
        )
        return [dict(row._mapping) for row in result]

    # ── Reporte productivo ───────────────────────────────────

    def total_milk_liters(self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None) -> Any:
        query = "SELECT COALESCE(SUM(quantity_liters), 0) AS total FROM milk_production WHERE farm_id = :farm_id"
        params: dict[str, Any] = {"farm_id": str(farm_id)}
        if start_date:
            query += " AND milking_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND milking_date <= :end_date"
            params["end_date"] = end_date
        return self._db.execute(text(query), params).scalar() or 0

    def milking_days(self, farm_id: uuid.UUID) -> int:
        """Días distintos con al menos un ordeño (mínimo 1)."""
        return int(
            self._db.execute(
                text("SELECT COUNT(DISTINCT DATE(milking_date)) FROM milk_production WHERE farm_id = :farm_id"),
                {"farm_id": str(farm_id)},
            ).scalar()
            or 1
        )

    def calves_by_age_group(self, farm_id: uuid.UUID) -> dict[str, int]:
        """Animales activos de hasta 2 años, agrupados por edad."""
        rows = self._db.execute(
            text("""
                SELECT
                    CASE
                        WHEN (CURRENT_DATE - birth_date) <= 90 THEN '0-3 meses'
                        WHEN (CURRENT_DATE - birth_date) <= 180 THEN '3-6 meses'
                        WHEN (CURRENT_DATE - birth_date) <= 365 THEN '6-12 meses'
                        ELSE '12+ meses'
                    END AS age_group,
                    COUNT(*) AS total
                FROM bovine
                WHERE farm_id = :farm_id AND is_active
                AND birth_date IS NOT NULL
                AND (CURRENT_DATE - birth_date) <= 730
                GROUP BY age_group
            """),
            {"farm_id": str(farm_id)},
        ).all()
        return {row[0]: row[1] for row in rows}

    # ── Reporte sanitario ────────────────────────────────────

    def treatments_by_type(self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None) -> dict[str, int]:
        query = """
            SELECT
                t.treatment_type,
                COUNT(*) AS total
            FROM treatment t
            WHERE t.farm_id = :farm_id
        """
        params: dict[str, Any] = {"farm_id": str(farm_id)}
        if start_date:
            query += " AND t.application_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND t.application_date <= :end_date"
            params["end_date"] = end_date
        query += " GROUP BY t.treatment_type"
        return {row[0]: row[1] for row in self._db.execute(text(query), params).all()}

    def pending_treatments(self, farm_id: uuid.UUID, today: date) -> int:
        """Tratamientos con una próxima aplicación programada para hoy o después."""
        return self._db.execute(
            text("SELECT COUNT(*) FROM treatment WHERE farm_id = :farm_id AND next_application_date >= :today"),
            {"farm_id": str(farm_id), "today": today},
        ).scalar() or 0

    def active_sanitary_plans(self, farm_id: uuid.UUID) -> int:
        return self._db.execute(
            text("SELECT COUNT(*) FROM sanitary_plan WHERE farm_id = :farm_id AND is_active"),
            {"farm_id": str(farm_id)},
        ).scalar() or 0

    # ── Reporte económico ────────────────────────────────────

    def economic_rows(self, farm_id: uuid.UUID, start_date: date | None, end_date: date | None) -> list[Any]:
        """Filas (ingreso, egreso, categoría) agrupadas por categoría y tipo."""
        query = """
            SELECT
                COALESCE(SUM(CASE WHEN er.record_type = 'ingreso' THEN er.amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN er.record_type IN ('egreso', 'gasto') THEN er.amount ELSE 0 END), 0) AS total_expense,
                er.category
            FROM economic_record er
            WHERE er.farm_id = :farm_id
        """
        params: dict[str, Any] = {"farm_id": str(farm_id)}
        if start_date:
            query += " AND er.record_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND er.record_date <= :end_date"
            params["end_date"] = end_date
        query += " GROUP BY er.category, er.record_type"
        return list(self._db.execute(text(query), params).all())
