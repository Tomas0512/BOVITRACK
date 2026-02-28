"""
Módulo: routers/auth.py
Descripción: Endpoints de autenticación — registro, login, refresh,
             olvidé contraseña y restablecer contraseña.
¿Para qué? Define las rutas HTTP que el frontend consume.
           Cada endpoint recibe un request, lo delega al service correspondiente,
           y retorna la respuesta con el status code adecuado.
¿Impacto? Estos son los puntos de entrada de la API de autenticación.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
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

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Crea una nueva cuenta de usuario en BoviTrack."""
    user = auth_service.register_user(db, user_data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
def login(
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
async def forgot_password(
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
