import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.audit_log import AuditLog
from app.models.farm import UserFarm
from app.models.role import Role
from app.models.user import User
from app.permissions import require_permission
from app.schemas.user import DeleteAccountRequest, MessageResponse, UserResponse
from app.services.audit_service import add_audit_log

router = APIRouter(prefix="/api/v1/users", tags=["Usuarios"])


# ── Schema para la respuesta de audit log ──────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    entity: str
    entity_id: str | None
    details: str | None
    created_at: datetime
    user_email: str | None = None
    user_full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Retorna los datos del usuario autenticado."""
    role_stmt = (
        select(Role.name)
        .join(UserFarm, UserFarm.role_id == Role.id)
        .where(UserFarm.user_id == current_user.id, UserFarm.is_active.is_(True), Role.is_active.is_(True))
        .order_by(UserFarm.assigned_at.desc())
        .limit(1)
    )
    role_name = db.execute(role_stmt).scalar_one_or_none()

    payload = UserResponse.model_validate(current_user).model_dump()
    payload["role_name"] = role_name
    return UserResponse(**payload)


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Eliminar cuenta propia",
)
def delete_my_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if data.confirmation_text.strip().upper() != "ELIMINAR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe confirmar escribiendo ELIMINAR",
        )

    add_audit_log(
        db,
        user_id=str(current_user.id),
        action="delete_account",
        entity="user",
        entity_id=str(current_user.id),
    )
    current_user.is_active = False
    current_user.token_version += 1
    db.commit()
    return MessageResponse(message="Cuenta desactivada exitosamente")


# ── Audit logs por finca ───────────────────────────────────────────────────────

audit_router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/audit-logs",
    tags=["Auditoría"],
)


@audit_router.get(
    "",
    response_model=list[AuditLogResponse],
    summary="Listar registros de auditoría de la finca",
    dependencies=[Depends(require_permission("usuarios", "can_read"))],
)
def list_audit_logs(
    farm_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AuditLogResponse]:
    """Retorna los registros de auditoría de los usuarios vinculados a la finca."""
    # Obtener IDs de todos los usuarios alguna vez vinculados a la finca
    member_ids = db.execute(
        select(UserFarm.user_id).where(UserFarm.farm_id == farm_id)
    ).scalars().all()

    if not member_ids:
        return []

    logs = db.execute(
        select(AuditLog)
        .where(AuditLog.user_id.in_(member_ids))
        .order_by(AuditLog.created_at.desc())
        .limit(200)
    ).scalars().all()

    result: list[AuditLogResponse] = []
    user_cache: dict[uuid.UUID, User] = {}
    for log in logs:
        usr = None
        if log.user_id:
            if log.user_id not in user_cache:
                usr = db.get(User, log.user_id)
                if usr:
                    user_cache[log.user_id] = usr
            usr = user_cache.get(log.user_id)

        result.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity=log.entity,
            entity_id=log.entity_id,
            details=log.details,
            created_at=log.created_at,
            user_email=usr.email if usr else None,
            user_full_name=f"{usr.first_name} {usr.last_name}" if usr else None,
        ))
    return result
