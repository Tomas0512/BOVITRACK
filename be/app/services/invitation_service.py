"""
Módulo: services/invitation_service.py
Lógica de negocio para el flujo de invitación de empleados a fincas.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm, UserFarm
from app.models.farm_invitation import FarmInvitation
from app.models.role import Role
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationInfo, InvitationResponse, InvitedRegister
from app.services.audit_service import add_audit_log
from app.utils.email import send_farm_invitation_email
from app.utils.security import hash_password

INVITATION_EXPIRE_HOURS = 72


async def create_invitation(
    db: Session,
    farm_id: uuid.UUID,
    data: InvitationCreate,
    invited_by: uuid.UUID,
) -> InvitationResponse:
    """Crea una invitación y envía email al empleado."""
    # Validar que la finca existe
    farm = db.execute(select(Farm).where(Farm.id == farm_id)).scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finca no encontrada")

    # Validar rol
    role = db.execute(select(Role).where(Role.id == data.role_id)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    email = data.email.lower().strip()

    # Si el usuario ya está registrado y ya está asignado a la finca → error
    existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing_user:
        existing_uf = db.execute(
            select(UserFarm).where(UserFarm.user_id == existing_user.id, UserFarm.farm_id == farm_id)
        ).scalar_one_or_none()
        if existing_uf:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este usuario ya está asignado a la finca")

    # Invalidar invitaciones previas no usadas para el mismo email + finca
    prev_invitations = db.execute(
        select(FarmInvitation).where(
            FarmInvitation.email == email,
            FarmInvitation.farm_id == farm_id,
            FarmInvitation.used.is_(False),
        )
    ).scalars().all()
    for prev in prev_invitations:
        prev.used = True

    token = str(uuid.uuid4())
    invitation = FarmInvitation(
        farm_id=farm_id,
        email=email,
        token=token,
        role_id=data.role_id,
        invited_by=invited_by,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=INVITATION_EXPIRE_HOURS),
    )
    db.add(invitation)

    add_audit_log(
        db,
        user_id=str(invited_by),
        action="employee_invited",
        entity="farm_invitation",
        entity_id=str(invitation.id),
        details={"email": email, "farm_id": str(farm_id), "role_id": str(data.role_id)},
    )
    db.commit()
    db.refresh(invitation)

    await send_farm_invitation_email(email=email, token=token, farm_name=farm.name)

    return InvitationResponse(
        id=invitation.id,
        farm_id=invitation.farm_id,
        email=invitation.email,
        role_id=invitation.role_id,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
    )


def get_invitation_info(db: Session, token: str) -> InvitationInfo:
    """Retorna la info pública de una invitación para mostrar en el formulario."""
    invitation = _get_valid_invitation(db, token)

    farm = db.execute(select(Farm).where(Farm.id == invitation.farm_id)).scalar_one()
    role = db.execute(select(Role).where(Role.id == invitation.role_id)).scalar_one()
    inviter = None
    if invitation.invited_by:
        inviter_user = db.execute(select(User).where(User.id == invitation.invited_by)).scalar_one_or_none()
        if inviter_user:
            inviter = f"{inviter_user.first_name} {inviter_user.last_name}"

    return InvitationInfo(
        email=invitation.email,
        farm_name=farm.name,
        role_name=role.name,
        inviter_name=inviter,
    )


def register_invited_user(db: Session, data: InvitedRegister) -> User:
    """Registra un usuario invitado y lo asigna a la finca."""
    invitation = _get_valid_invitation(db, data.token)

    # Validar que no exista ya un usuario con ese email
    existing = db.execute(select(User).where(User.email == invitation.email)).scalar_one_or_none()
    if existing:
        # Si ya existe, solo asignarlo a la finca
        _assign_to_farm(db, existing, invitation)
        return existing

    # Validar datos
    _validate_registration_data(data)

    # Verificar documento duplicado
    existing_doc = db.execute(
        select(User).where(User.document_number == data.document_number.strip())
    ).scalar_one_or_none()
    if existing_doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de documento ya está registrado")

    # Crear usuario
    new_user = User(
        email=invitation.email,
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        document_type=data.document_type,
        document_number=data.document_number.strip(),
        phone=data.phone.strip(),
        hashed_password=hash_password(data.password),
        email_verified=True,  # Verificado por invitación
        accepted_terms=data.accept_terms,
        accepted_data_policy=data.accept_data_policy,
        accepted_terms_at=datetime.now(timezone.utc) if data.accept_terms else None,
        accepted_data_policy_at=datetime.now(timezone.utc) if data.accept_data_policy else None,
    )
    db.add(new_user)
    db.flush()

    _assign_to_farm(db, new_user, invitation)

    add_audit_log(
        db,
        user_id=str(new_user.id),
        action="register_by_invitation",
        entity="user",
        entity_id=str(new_user.id),
        details={"email": new_user.email, "farm_id": str(invitation.farm_id)},
    )
    db.commit()
    db.refresh(new_user)

    return new_user


def _get_valid_invitation(db: Session, token: str) -> FarmInvitation:
    """Obtiene y valida una invitación por token."""
    invitation = db.execute(
        select(FarmInvitation).where(FarmInvitation.token == token)
    ).scalar_one_or_none()

    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada")
    if invitation.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta invitación ya fue utilizada")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La invitación ha expirado")

    return invitation


def _assign_to_farm(db: Session, user: User, invitation: FarmInvitation) -> None:
    """Asigna el usuario a la finca y marca la invitación como usada."""
    # Verificar que no esté ya asignado
    existing = db.execute(
        select(UserFarm).where(UserFarm.user_id == user.id, UserFarm.farm_id == invitation.farm_id)
    ).scalar_one_or_none()
    if existing:
        invitation.used = True
        return

    uf = UserFarm(
        user_id=user.id,
        farm_id=invitation.farm_id,
        role_id=invitation.role_id,
        assigned_by=invitation.invited_by,
        is_active=True,
    )
    db.add(uf)
    invitation.used = True


def _validate_registration_data(data: InvitedRegister) -> None:
    """Valida los datos de registro del invitado."""
    if not data.accept_terms:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe aceptar términos y condiciones")
    if not data.accept_data_policy:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe autorizar tratamiento de datos")

    if len(data.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe contener al menos una mayúscula")
    if not re.search(r"[a-z]", data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe contener al menos una minúscula")
    if not re.search(r"\d", data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe contener al menos un número")
    if not re.search(r"[^A-Za-z0-9]", data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe contener al menos un carácter especial")
