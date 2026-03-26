from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.farm import UserFarm
from app.models.role import Role
from app.models.user import User
from app.schemas.user import DeleteAccountRequest, MessageResponse, UserResponse
from app.services.audit_service import add_audit_log

router = APIRouter(prefix="/api/v1/users", tags=["Usuarios"])


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
