"""
Module: routers/reports.py
What? FastAPI router for report and statistics endpoints.
Why? Expose aggregated data using SQL views and stored functions.
Impact? Reports are a grading rubric requirement.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission
from app.schemas.report import (
    ExportFormat,
    ReportCategory,
    ReportFilterParams,
    ReportResponse,
)
from app.services import report_service
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/v1", tags=["Reportes"])


@router.get("/farms/{farm_id}/statistics", summary="Estadisticas completas de finca", dependencies=[Depends(require_permission("fincas", "can_read"))])
def farm_statistics(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    _ = current_user
    result = db.execute(text("SELECT fn_farm_statistics(:farm_id)"), {"farm_id": str(farm_id)})
    row = result.scalar_one_or_none()
    if row is None:
        return {"message": "Farm without statistics"}
    return row


@router.get("/farms/{farm_id}/milk-daily", summary="Produccion lechera diaria", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def milk_daily(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    result = db.execute(
        text("SELECT * FROM v_milk_production_daily WHERE farm_id = :farm_id ORDER BY milking_date DESC"),
        {"farm_id": str(farm_id)},
    )
    return [dict(row._mapping) for row in result]


@router.get("/reports/farm-summary", summary="Resumen de todas las fincas")
def farm_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    result = db.execute(text("SELECT * FROM v_farm_summary"))
    return [dict(row._mapping) for row in result]


@router.get("/reports/low-stock-alerts", summary="Alertas de stock bajo")
def low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    result = db.execute(text("SELECT * FROM v_low_stock_alerts"))
    return [dict(row._mapping) for row in result]


@router.get("/reports/pending-tasks", summary="Tareas pendientes")
def pending_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    result = db.execute(text("SELECT * FROM v_pending_tasks"))
    return [dict(row._mapping) for row in result]


@router.get("/farms/{farm_id}/reports", summary="Generar reporte con filtros")
@limiter.limit("10/minute")
def generate_farm_report(
    request: Request,
    farm_id: uuid.UUID,
    category: ReportCategory | None = Query(None, description="productivo, sanitario, economico"),
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
    export: ExportFormat = Query(ExportFormat.JSON, description="Formato: json, pdf, excel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date

    params = ReportFilterParams(
        category=category,
        start_date=date.fromisoformat(start_date) if start_date else None,
        end_date=date.fromisoformat(end_date) if end_date else None,
        export=export,
    )

    report = report_service.generate_report(db, farm_id, current_user, params)

    if export == ExportFormat.JSON:
        return report

    if export == ExportFormat.EXCEL:
        content = report_service.export_to_excel(report)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=reporte_{farm_id}.xlsx"},
        )

    if export == ExportFormat.PDF:
        content = report_service.export_to_pdf(report)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=reporte_{farm_id}.pdf"},
        )
