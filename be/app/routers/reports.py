"""
Module: routers/reports.py
What? FastAPI router for report and statistics endpoints.
Why? Expose aggregated data using SQL views and stored functions.
Impact? Reports are a grading rubric requirement.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.farm import Farm, UserFarm
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


def _accessible_farm_ids(db: Session, user_id: uuid.UUID) -> list[str]:
    """¿Qué? Devuelve los ids (como str) de las fincas activas del usuario.

    Considera tanto las fincas donde el usuario es propietario como aquellas
    donde está registrado como miembro activo (UserFarm). Se usa para acotar
    las consultas globales a las fincas del usuario y evitar fugas entre fincas.
    """
    owner_stmt = select(Farm.id).where(
        Farm.owner_id == user_id,
        Farm.is_active.is_(True),
    )
    member_stmt = select(UserFarm.farm_id).where(
        UserFarm.user_id == user_id,
        UserFarm.is_active.is_(True),
    )
    ids: set[str] = set()
    ids.update(str(x) for x in db.execute(owner_stmt).scalars().all())
    ids.update(str(x) for x in db.execute(member_stmt).scalars().all())
    return sorted(ids)


def _query_view_filtered(db: Session, user_id: uuid.UUID, view: str) -> list[dict]:
    """¿Qué? Consulta una vista de reporte acotada a las fincas del usuario."""
    farm_ids = _accessible_farm_ids(db, user_id)
    if not farm_ids:
        return []
    placeholders = ",".join(f":f{i}" for i in range(len(farm_ids)))
    params = {f"f{i}": fid for i, fid in enumerate(farm_ids)}
    result = db.execute(
        text(f"SELECT * FROM {view} WHERE farm_id IN ({placeholders})"),
        params,
    )
    return [dict(row._mapping) for row in result]


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
    return _query_view_filtered(db, current_user.id, "v_farm_summary")


@router.get("/reports/low-stock-alerts", summary="Alertas de stock bajo")
def low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    return _query_view_filtered(db, current_user.id, "v_low_stock_alerts")


@router.get("/reports/pending-tasks", summary="Tareas pendientes")
def pending_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    _ = current_user
    return _query_view_filtered(db, current_user.id, "v_pending_tasks")


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
    current_user: User = Depends(require_permission("fincas", "can_read")),
):
    from datetime import date

    params = ReportFilterParams(
        category=category,
        start_date=date.fromisoformat(start_date) if start_date else None,
        end_date=date.fromisoformat(end_date) if end_date else None,
        export=export,
    )

    # ¿Qué? Validar coherencia de fechas (no lógicas) antes de generar.
    if params.start_date and params.end_date and params.start_date > params.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha inicial no puede ser posterior a la final",
        )
    today = date.today()
    if params.start_date and params.start_date > today:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha inicial no puede ser futura",
        )
    if params.end_date and params.end_date > today:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha final no puede ser futura",
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
