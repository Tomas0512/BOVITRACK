import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.reactivation import ReactivationRequestDetail, ReactivationRequestResponse
from app.schemas.user import MessageResponse
from app.services import reactivation_service

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])


@router.get(
    "/reactivation-requests",
    response_model=list[ReactivationRequestDetail],
    summary="Listar solicitudes de reactivación pendientes",
)
def list_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
) -> ReactivationRequestResponse:
    req = reactivation_service.reject_request(db, request_id, current_user.id)
    return ReactivationRequestResponse.model_validate(req)
