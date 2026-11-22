"""
Módulo: modules/identity/router.py (frontera HTTP del módulo)
¿Qué? Endpoints de autenticación (/api/v1/auth) y de la cuenta propia (/api/v1/users/me).
¿Para qué? Recibir la petición, delegar en el servicio y responder. Ninguna regla de
           negocio vive aquí: los errores de dominio se traducen a HTTP en
           app.core.error_handlers.
¿Impacto? Las rutas, los nombres de las funciones (operationId) y los docstrings
          (descripciones de OpenAPI) son los mismos que antes del refactor.
          Las rutas públicas de invitación y reactivación (mismo prefijo) son
          del módulo team.
"""

from fastapi import APIRouter, Depends, Request, status

from app.core.limiter import limiter
from app.modules.identity.dependencies import get_account_service, get_auth_service, get_current_user
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    DeleteAccountRequest,
    ForgotPasswordRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.modules.identity.service import AccountService, AuthService

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])
users_router = APIRouter(prefix="/api/v1/users", tags=["Usuarios"])


# ═══════════════════════════════════════════════════════════════
# Autenticación
# ═══════════════════════════════════════════════════════════════


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Crea una nueva cuenta de usuario en BoviTrack."""
    user = service.register(user_data)
    await service.send_verification_email(user.id)
    return UserResponse.model_validate(user)


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
@limiter.limit("10/minute")
def login(
    request: Request,
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Autentica al usuario y retorna access + refresh tokens."""
    return service.login(credentials)


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
)
@limiter.limit("10/minute")
def refresh(
    request: Request,
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Genera un nuevo par de tokens a partir de un refresh token válido."""
    return service.refresh(data.refresh_token)


@auth_router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Solicitar recuperación de contraseña",
)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Envía un correo con el enlace de recuperación de contraseña."""
    await service.request_password_reset(data.email)
    return MessageResponse(
        message="Si el correo está registrado, recibirás un enlace para restablecer tu contraseña"
    )


@auth_router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Restablecer contraseña",
)
@limiter.limit("5/minute")
def reset_password_endpoint(
    request: Request,
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Restablece la contraseña usando el token de recuperación."""
    service.reset_password(data)
    return MessageResponse(message="Contraseña restablecida exitosamente")


@auth_router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verificar correo electrónico",
)
@limiter.limit("5/minute")
def verify_email(
    request: Request,
    token: str,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    service.verify_email(token)
    return MessageResponse(message="Correo verificado exitosamente")


@auth_router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Cerrar sesión en todos los dispositivos",
)
def logout_all(
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    service.logout_all(current_user)
    return MessageResponse(message="Sesiones cerradas en todos los dispositivos")


# ═══════════════════════════════════════════════════════════════
# Cuenta propia
# ═══════════════════════════════════════════════════════════════


@users_router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> UserResponse:
    """Retorna los datos del usuario autenticado."""
    return service.profile(current_user)


@users_router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Eliminar cuenta propia",
)
def delete_my_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> MessageResponse:
    service.delete_account(current_user, data.confirmation_text)
    return MessageResponse(message="Cuenta desactivada exitosamente")


# Router del módulo: autenticación + cuenta propia.
router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
