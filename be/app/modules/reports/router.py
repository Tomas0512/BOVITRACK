"""
Módulo: modules/reports/router.py (frontera HTTP del módulo)
¿Qué? Endpoints de reportes y estadísticas:
      - /api/v1/farms/{farm_id}/statistics y /milk-daily (por finca)
      - /api/v1/reports/farm-summary, /low-stock-alerts, /pending-tasks (todas las fincas del usuario)
      - /api/v1/farms/{farm_id}/reports (reporte filtrado; JSON, Excel o PDF)
¿Para qué? Traducir HTTP <-> ReportService: parsear parámetros, exigir permisos
           y armar la respuesta de descarga con su tipo de contenido.
¿Impacto? Sin SQL ni reglas de negocio (antes este router consultaba la BD y
          validaba fechas; ahora lo hacen el repositorio y el servicio).
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response

from app.core.limiter import limiter
from app.modules.reports.dependencies import get_current_user, get_report_service, require_permission
from app.modules.reports.schemas import ExportFormat, ReportCategory, ReportFilterParams
from app.modules.reports.service import ReportService
from app.shared.exceptions import InvalidRequestError
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1", tags=["Reportes"])

INVALID_DATE = "Fecha inválida en '{field}': use el formato YYYY-MM-DD"


def _parse_date(value: str | None, field: str) -> date | None:
    """Convierte 'YYYY-MM-DD' en date. Un formato inválido responde 422 (antes daba 500)."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidRequestError(INVALID_DATE.format(field=field)) from exc


@router.get("/farms/{farm_id}/statistics", summary="Estadisticas completas de finca", dependencies=[Depends(require_permission("fincas", "can_read"))])
def farm_statistics(
    farm_id: uuid.UUID,
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    _ = current_user
    return service.farm_statistics(farm_id)


@router.get("/farms/{farm_id}/milk-daily", summary="Produccion lechera diaria", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def milk_daily(
    farm_id: uuid.UUID,
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    return service.milk_daily(farm_id)


@router.get("/reports/farm-summary", summary="Resumen de todas las fincas")
def farm_summary(
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    return service.view_for_user(current_user.id, "v_farm_summary")


@router.get("/reports/low-stock-alerts", summary="Alertas de stock bajo")
def low_stock_alerts(
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    return service.view_for_user(current_user.id, "v_low_stock_alerts")


@router.get("/reports/pending-tasks", summary="Tareas pendientes")
def pending_tasks(
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    return service.view_for_user(current_user.id, "v_pending_tasks")


@router.get("/farms/{farm_id}/reports", summary="Generar reporte con filtros")
@limiter.limit("10/minute")
def generate_farm_report(
    request: Request,
    farm_id: uuid.UUID,
    category: ReportCategory | None = Query(None, description="productivo, sanitario, economico"),
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
    export: ExportFormat = Query(ExportFormat.JSON, description="Formato: json, pdf, excel"),
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(require_permission("fincas", "can_read")),
):
    _ = current_user
    params = ReportFilterParams(
        category=category,
        start_date=_parse_date(start_date, "start_date"),
        end_date=_parse_date(end_date, "end_date"),
        export=export,
    )
    report = service.generate_report(farm_id, params)

    if export == ExportFormat.JSON:
        return report

    if export == ExportFormat.EXCEL:
        return Response(
            content=service.export_to_excel(report),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=reporte_{farm_id}.xlsx"},
        )

    if export == ExportFormat.PDF:
        return Response(
            content=service.export_to_pdf(report),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=reporte_{farm_id}.pdf"},
        )
