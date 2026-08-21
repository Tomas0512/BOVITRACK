"""
Módulo: routers/audit.py
HU015 - Revisión de auditorías del sistema (Sprint 8 - Camilo)

COMO: Administrador del sistema
QUIERO: un endpoint que me permita consultar la auditoría filtrando por
        usuario, acción, entidad, finca y rango de fechas
PARA:   rastrear quién modificó qué información y cuándo, y sustentar
        cualquier revisión o reclamo sobre los datos de la finca.

Endpoints expuestos:
  GET /api/v1/admin/audit-logs         → Listado paginado con filtros
  GET /api/v1/admin/audit-logs/actions → Catálogo de acciones y entidades
  GET /api/v1/admin/audit-logs/export  → Descarga en CSV o Excel

¿Impacto de seguridad?
  El endpoint NO recibe farm_id en la ruta, por lo que no puede usarse la
  dependencia `require_permission(...)` (que lo exige como Path param). En su
  lugar se valida el permiso `usuarios:can_read` sobre al menos una finca del
  usuario, y el servicio acota SIEMPRE los resultados a esas mismas fincas.
  Así ningún usuario puede leer la auditoría de una finca ajena.
"""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.audit_log import AuditLog
from app.models.farm import UserFarm
from app.models.role import Permission
from app.models.user import User
from app.schemas.audit import AuditExportFormat, AuditLogFilters, AuditLogPage
from app.services import audit_service

router = APIRouter(prefix="/api/v1/admin/audit-logs", tags=["Auditoría"])


def require_audit_reader(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """¿Qué? Dependencia que autoriza la lectura de auditoría.

    COMO: dueño del sistema
    QUIERO: que solo los roles con permiso de lectura sobre usuarios puedan
            entrar al módulo de auditoría
    PARA:   que un empleado raso no pueda revisar la actividad de sus
            compañeros ni de la administración.

    ¿Impacto? Responde 403 si el usuario no tiene `usuarios:can_read` en
              ninguna de sus fincas activas.
    """
    stmt = (
        select(Permission.id)
        .join(UserFarm, UserFarm.role_id == Permission.role_id)
        .where(
            UserFarm.user_id == current_user.id,
            UserFarm.is_active.is_(True),
            Permission.module == "usuarios",
            Permission.can_read.is_(True),
        )
        .limit(1)
    )

    if db.execute(stmt).scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar la auditoría del sistema",
        )

    return current_user


@router.get(
    "",
    response_model=AuditLogPage,
    summary="Consultar auditoría del sistema con filtros",
)
def list_audit_logs(
    user_id: uuid.UUID | None = Query(None, description="Usuario que ejecutó la acción"),
    farm_id: uuid.UUID | None = Query(None, description="Finca a consultar"),
    action: str | None = Query(None, max_length=100, description="Acción (coincidencia parcial)"),
    entity: str | None = Query(None, max_length=100, description="Entidad (coincidencia parcial)"),
    start_date: date | None = Query(None, description="Fecha inicial inclusive (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Fecha final inclusive (YYYY-MM-DD)"),
    include_auth_events: bool = Query(True, description="Incluir login/logout/registro"),
    limit: int = Query(100, ge=1, le=500, description="Registros por página"),
    offset: int = Query(0, ge=0, description="Registros a omitir"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_audit_reader),
) -> AuditLogPage:
    """¿Qué? Retorna la auditoría filtrada y paginada.

    COMO: Administrador
    QUIERO: aplicar uno o varios filtros combinados sobre la auditoría
    PARA:   aislar exactamente el evento que estoy investigando en vez de
            recorrer manualmente cientos de registros.

    ¿Impacto? Sin filtros retorna los 100 registros más recientes de las
              fincas del usuario, junto con el total disponible para paginar.
    """
    filters = AuditLogFilters(
        user_id=user_id,
        farm_id=farm_id,
        action=action,
        entity=entity,
        start_date=start_date,
        end_date=end_date,
        include_auth_events=include_auth_events,
    )

    return audit_service.list_audit_logs(
        db,
        current_user_id=current_user.id,
        filters=filters,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/actions",
    response_model=dict[str, list[str]],
    summary="Catálogo de acciones y entidades registradas",
)
def list_audit_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_audit_reader),
) -> dict[str, list[str]]:
    """¿Qué? Devuelve los valores distintos de `action` y `entity` existentes.

    COMO: Administrador usando la pantalla de auditoría
    QUIERO: que los filtros de acción y entidad sean listas desplegables
    PARA:   no tener que adivinar ni escribir a mano nombres técnicos como
            'create_bovine' y arriesgarme a filtrar sin resultados.

    ¿Impacto? Solo considera las fincas accesibles al usuario, de modo que el
              catálogo no revela actividad de fincas ajenas.
    """
    accessible_farm_ids = audit_service.get_accessible_farm_ids(db, current_user.id)

    if not accessible_farm_ids:
        return {"actions": [], "entities": []}

    actions = db.execute(
        select(AuditLog.action)
        .where(AuditLog.farm_id.in_(accessible_farm_ids))
        .distinct()
        .order_by(AuditLog.action)
    ).scalars().all()

    entities = db.execute(
        select(AuditLog.entity)
        .where(AuditLog.farm_id.in_(accessible_farm_ids))
        .distinct()
        .order_by(AuditLog.entity)
    ).scalars().all()

    return {"actions": list(actions), "entities": list(entities)}


@router.get(
    "/export",
    summary="Exportar la auditoría filtrada a CSV o Excel",
    response_class=Response,
)
def export_audit_logs(
    export: AuditExportFormat = Query(
        AuditExportFormat.EXCEL,
        description="Formato del archivo: csv o excel",
    ),
    user_id: uuid.UUID | None = Query(None, description="Usuario que ejecutó la acción"),
    farm_id: uuid.UUID | None = Query(None, description="Finca a consultar"),
    action: str | None = Query(None, max_length=100, description="Acción (coincidencia parcial)"),
    entity: str | None = Query(None, max_length=100, description="Entidad (coincidencia parcial)"),
    start_date: date | None = Query(None, description="Fecha inicial inclusive (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Fecha final inclusive (YYYY-MM-DD)"),
    include_auth_events: bool = Query(True, description="Incluir login/logout/registro"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_audit_reader),
) -> Response:
    """¿Qué? Descarga la auditoría filtrada como archivo CSV o Excel.

    COMO: Administrador del sistema
    QUIERO: descargar exactamente los registros que estoy viendo con mis
            filtros aplicados
    PARA:   conservar la evidencia fuera del sistema, adjuntarla a un informe
            o entregarla a un tercero sin darle acceso a la aplicación.

    ¿Impacto? Acepta los mismos filtros que el listado, pero NO pagina: exporta
              todos los registros que los cumplen (hasta el tope definido en
              `audit_service.EXPORT_MAX_ROWS`), de modo que el archivo no quede
              recortado a la página visible en pantalla.

    ¿Formato JSON? Se rechaza con 400: para consultar en JSON existe el
              endpoint de listado, que además entrega la paginación.
    """
    if export == AuditExportFormat.JSON:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para consultar en JSON usa GET /api/v1/admin/audit-logs",
        )

    filters = AuditLogFilters(
        user_id=user_id,
        farm_id=farm_id,
        action=action,
        entity=entity,
        start_date=start_date,
        end_date=end_date,
        include_auth_events=include_auth_events,
    )

    records = audit_service.collect_logs_for_export(
        db,
        current_user_id=current_user.id,
        filters=filters,
    )

    # Nombre con la fecha de descarga para no sobrescribir archivos anteriores.
    stamp = date.today().isoformat()

    if export == AuditExportFormat.CSV:
        return Response(
            content=audit_service.export_to_csv(records),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=auditoria_{stamp}.csv"
            },
        )

    return Response(
        content=audit_service.export_to_excel(records),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=auditoria_{stamp}.xlsx"
        },
    )
