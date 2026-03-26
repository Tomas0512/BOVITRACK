"""
Módulo: routers/auth.py
Descripción: Endpoints de autenticación — registro, login, refresh,
             olvidé contraseña y restablecer contraseña.
¿Para qué? Define las rutas HTTP que el frontend consume.
           Cada endpoint recibe un request, lo delega al service correspondiente,
           y retorna la respuesta con el status code adecuado.
¿Impacto? Estos son los puntos de entrada de la API de autenticación.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services import auth_service
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Crea una nueva cuenta de usuario en BoviTrack."""
    user = auth_service.register_user(db, user_data)
    await auth_service.send_registration_verification_email(db, user.id)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
@limiter.limit("10/minute")
def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Autentica al usuario y retorna access + refresh tokens."""
    return auth_service.login_user(db, credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Genera un nuevo par de tokens a partir de un refresh token válido."""
    return auth_service.refresh_access_token(db, data.refresh_token)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Solicitar recuperación de contraseña",
)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Envía un correo con el enlace de recuperación de contraseña."""
    await auth_service.request_password_reset(db, data.email)
    return MessageResponse(
        message="Si el correo está registrado, recibirás un enlace para restablecer tu contraseña"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Restablecer contraseña",
)
def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Restablece la contraseña usando el token de recuperación."""
    auth_service.reset_password(db, data)
    return MessageResponse(message="Contraseña restablecida exitosamente")


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verificar correo electrónico",
)
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    auth_service.verify_email_token(db, token)
    return MessageResponse(message="Correo verificado exitosamente")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Cerrar sesión en todos los dispositivos",
)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    auth_service.logout_all_sessions(db, current_user)
    return MessageResponse(message="Sesiones cerradas en todos los dispositivos")
