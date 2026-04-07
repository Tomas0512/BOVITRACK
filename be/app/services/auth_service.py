"""
Módulo: services/auth_service.py
Descripción: Lógica de negocio para todas las operaciones de autenticación —
             registro, login, cambio de contraseña y recuperación.
¿Para qué? Separar la lógica de negocio de los endpoints (routers). Los routers solo
           reciben requests y llaman al service; el service contiene TODA la lógica.
¿Impacto? Este módulo es el cerebro del sistema de auth. Aquí se decide si un login
          es válido, si un registro debe aceptarse, y cómo se maneja cada flujo.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User
from app.services.audit_service import add_audit_log
from app.schemas.user import (
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.utils.email import send_password_reset_email
from app.utils.email import send_email_verification
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def register_user(db: Session, user_data: UserCreate) -> User:
    """Registra un nuevo usuario en el sistema.

    Flujo: verifica email/documento duplicado → hashea password → crea en BD.
    """
    # Verificar si el email ya existe
    stmt = select(User).where(User.email == user_data.email.lower().strip())
    existing_user = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    # Verificar si el documento ya existe
    stmt = select(User).where(
        User.document_number == user_data.document_number.strip()
    )
    existing_doc = db.execute(stmt).scalar_one_or_none()

    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de documento ya está registrado",
        )

    new_user = User(
        email=user_data.email.lower().strip(),
        first_name=user_data.first_name.strip(),
        last_name=user_data.last_name.strip(),
        document_type=user_data.document_type.value,
        document_number=user_data.document_number.strip(),
        phone=user_data.phone.strip(),
        hashed_password=hash_password(user_data.password),
        accepted_terms=user_data.accept_terms,
        accepted_data_policy=user_data.accept_data_policy,
        accepted_terms_at=datetime.now(timezone.utc) if user_data.accept_terms else None,
        accepted_data_policy_at=datetime.now(timezone.utc) if user_data.accept_data_policy else None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = str(uuid.uuid4())
    db.add(
        EmailVerificationToken(
            user_id=new_user.id,
            token=verification_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
    )
    db.commit()

    add_audit_log(
        db,
        user_id=str(new_user.id),
        action="register",
        entity="user",
        entity_id=str(new_user.id),
        details={"email": new_user.email},
    )
    db.commit()

    return new_user


def login_user(db: Session, login_data: UserLogin) -> TokenResponse:
    """Autentica un usuario y retorna tokens JWT.

    Flujo: buscar por email → verificar password → generar tokens.
    """
    stmt = select(User).where(User.email == login_data.email.lower().strip())
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacte al administrador.",
        )

    token_payload = {"sub": str(user.id), "ver": user.token_version}
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)

    add_audit_log(
        db,
        user_id=str(user.id),
        action="login",
        entity="user",
        entity_id=str(user.id),
        details={"email": user.email},
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    """Genera nuevos tokens usando un refresh token válido."""
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
        )

    stmt = select(User).where(User.id == uuid.UUID(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o cuenta desactivada",
        )

    token_payload = {"sub": str(user.id), "ver": user.token_version}
    new_access = create_access_token(data=token_payload)
    new_refresh = create_refresh_token(data=token_payload)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )


async def request_password_reset(db: Session, email: str) -> None:
    """Solicita un email de recuperación de contraseña.

    SIEMPRE retorna éxito, incluso si el email no existe en la BD.
    Esto previene la enumeración de usuarios.
    """
    stmt = select(User).where(User.email == email.lower().strip())
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return

    reset_token = str(uuid.uuid4())

    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    db.add(token_record)
    db.commit()

    await send_password_reset_email(email=user.email, token=reset_token)


def reset_password(db: Session, reset_data: ResetPasswordRequest) -> None:
    """Restablece la contraseña usando un token de recuperación."""
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token == reset_data.token
    )
    token_record = db.execute(stmt).scalar_one_or_none()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido",
        )

    if token_record.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token de recuperación ya fue utilizado",
        )

    if token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de recuperación ha expirado. Solicite uno nuevo.",
        )

    stmt = select(User).where(User.id == token_record.user_id)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )

    user.hashed_password = hash_password(reset_data.new_password)
    token_record.used = True
    add_audit_log(
        db,
        user_id=str(user.id),
        action="password_reset",
        entity="user",
        entity_id=str(user.id),
    )
    db.commit()


async def send_registration_verification_email(db: Session, user_id: uuid.UUID) -> None:
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return

    token = str(uuid.uuid4())
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
    )
    db.commit()
    await send_email_verification(user.email, token)


def verify_email_token(db: Session, token: str) -> None:
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    token_row = db.execute(stmt).scalar_one_or_none()

    if not token_row or token_row.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de verificación inválido")
    if token_row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de verificación expirado")

    user = db.execute(select(User).where(User.id == token_row.user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")

    user.email_verified = True
    token_row.used = True
    add_audit_log(
        db,
        user_id=str(user.id),
        action="email_verified",
        entity="user",
        entity_id=str(user.id),
    )
    db.commit()


def logout_all_sessions(db: Session, user: User) -> None:
    user.token_version += 1
    add_audit_log(
        db,
        user_id=str(user.id),
        action="logout_all_sessions",
        entity="user",
        entity_id=str(user.id),
    )
    db.commit()
