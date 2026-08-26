import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.farm import UserFarm
from app.models.role import Role
from app.models.user import User
from app.schemas.reactivation import ReactivationRequestDetail, ReactivationRequestResponse
from app.schemas.user import MessageResponse
from app.services import reactivation_service

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])


def require_admin_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """¿Qué? Dependencia que autoriza la gestión de reactivaciones.

    ¿Para qué? Solo los usuarios con rol Administrador activo en al menos una
               finca pueden listar, aprobar o rechazar solicitudes de
               reactivación de cuentas. Evita que un usuario común (p. ej. un
               empleado) modere cuentas de terceros.

    ¿Impacto? Responde 403 si el usuario no es administrador.
    """
    stmt = (
        select(Role.id)
        .join(UserFarm, UserFarm.role_id == Role.id)
        .where(
            UserFarm.user_id == current_user.id,
            UserFarm.is_active.is_(True),
            Role.name == "Administrador",
            Role.is_active.is_(True),
        )
        .limit(1)
    )

    if db.execute(stmt).scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede gestionar solicitudes de reactivación",
        )

    return current_user


@router.get(
    "/reactivation-requests",
    response_model=list[ReactivationRequestDetail],
    summary="Listar solicitudes de reactivación pendientes",
)
def list_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
) -> list[ReactivationRequestDetail]:
    _ = current_user
    return reactivation_service.list_pending_requests(db)


@router.post(
    "/reactivation-requests/{request_id}/approve",
    response_model=ReactivationRequestResponse,
    summary="Aprobar solicitud de reactivación",
)
def approve(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
) -> ReactivationRequestResponse:
    req = reactivation_service.approve_request(db, request_id, current_user.id)
    return ReactivationRequestResponse.model_validate(req)


@router.post(
    "/reactivation-requests/{request_id}/reject",
    response_model=ReactivationRequestResponse,
    summary="Rechazar solicitud de reactivación",
)
def reject(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
) -> ReactivationRequestResponse:
    req = reactivation_service.reject_request(db, request_id, current_user.id)
    return ReactivationRequestResponse.model_validate(req)
