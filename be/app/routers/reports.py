"""
Módulo: routers/reports.py
¿Qué? Router de FastAPI para endpoints de reportes y estadísticas.
¿Para qué? Exponer datos agregados consumiendo las vistas SQL y funciones
           almacenadas creadas en las migraciones de Alembic.
¿Impacto? Los reportes son un requisito de la rúbrica de evaluación.
          Sin este router, las vistas SQL existirían pero no serían accesibles
          desde el frontend.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission

router = APIRouter(prefix="/api/v1", tags=["Reportes"])


@router.get("/farms/{farm_id}/statistics", summary="Estadísticas completas de finca", dependencies=[Depends(require_permission("fincas", "can_read"))])
def farm_statistics(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """¿Qué? Ejecuta la función SQL fn_farm_statistics y retorna JSON.
    ¿Para qué? Obtener métricas consolidadas de la finca: total bovinos,
               producción, tratamientos, inventario, etc.
    ¿Impacto? Los datos los calcula la BD (no Python) para mayor eficiencia.
              Si la finca no tiene datos, retorna un mensaje informativo.
    """
    _ = current_user
    result = db.execute(text("SELECT fn_farm_statistics(:farm_id)"), {"farm_id": str(farm_id)})
    row = result.scalar_one_or_none()
    if row is None:
        return {"message": "Finca sin estadísticas"}
    return row


@router.get("/farms/{farm_id}/milk-daily", summary="Producción lechera diaria", dependencies=[Depends(require_permission("produccion_leche", "can_read"))])
def milk_daily(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """¿Qué? Consulta la vista v_milk_production_daily filtrada por finca.
    ¿Para qué? Obtener la producción diaria agregada para gráficos en el dashboard.
    ¿Impacto? La vista agrupa por fecha y suma litros — el cálculo lo hace la BD.
    """
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
    """¿Qué? Consulta la vista v_farm_summary para un resumen general.
    ¿Para qué? Dashboard global con métricas de todas las fincas del usuario.
    ¿Impacto? La vista cruza datos de fincas, bovinos, potreros y producción.
    """
    _ = current_user
    result = db.execute(text("SELECT * FROM v_farm_summary"))
    return [dict(row._mapping) for row in result]


@router.get("/reports/low-stock-alerts", summary="Alertas de stock bajo")
def low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """¿Qué? Consulta la vista v_low_stock_alerts.
    ¿Para qué? Identificar alimentos cuyo stock actual está por debajo del mínimo.
    ¿Impacto? Permite al usuario reabastecerse antes de que se agoten los insumos.
    """
    _ = current_user
    result = db.execute(text("SELECT * FROM v_low_stock_alerts"))
    return [dict(row._mapping) for row in result]


@router.get("/reports/pending-tasks", summary="Tareas pendientes")
def pending_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """¿Qué? Consulta la vista v_pending_tasks.
    ¿Para qué? Mostrar tareas pendientes ordenadas por urgencia para el dashboard.
    ¿Impacto? La vista filtra automáticamente las tareas con status='pendiente'.
    """
    _ = current_user
    result = db.execute(text("SELECT * FROM v_pending_tasks"))
    return [dict(row._mapping) for row in result]
