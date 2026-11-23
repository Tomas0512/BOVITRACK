"""
Módulo: modules/team/router/public.py (frontera HTTP: rutas públicas de team)
¿Qué? Rutas SIN sesión bajo /api/v1/auth: ver una invitación, registrarse por
      invitación y pedir la reactivación de una cuenta.
¿Para qué? Comparten prefijo y tag con identity ("Autenticación") porque el
           cliente las usa en las pantallas de acceso; para él la API no cambió.
¿Impacto? Las reglas están en InvitationService y ReactivationService.
"""

from fastapi import APIRouter, Depends, Request, status

from app.core.limiter import limiter
from app.modules.team.dependencies import UserResponse, get_invitation_service, get_reactivation_service
from app.modules.team.schemas import (
    InvitationInfo,
    InvitedRegister,
    ReactivationRequestAccepted,
    ReactivationRequestCreate,
)
from app.modules.team.service import InvitationService, ReactivationService
from app.modules.team.service.reactivation import REQUEST_RECEIVED

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.get(
    "/invitation/{token}",
    response_model=InvitationInfo,
    summary="Obtener info de invitación",
)
def get_invitation(
    token: str,
    service: InvitationService = Depends(get_invitation_service),
) -> InvitationInfo:
    """Retorna la info pública de una invitación para mostrar en el formulario de registro."""
    return service.info(token)


@router.post(
    "/register-invited",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario por invitación",
)
@limiter.limit("5/minute")
def register_invited(
    request: Request,
    data: InvitedRegister,
    service: InvitationService = Depends(get_invitation_service),
) -> UserResponse:
    """Registra un nuevo usuario a partir de una invitación y lo asigna a la finca."""
    return UserResponse.model_validate(service.register_invited(data))


@router.post(
    "/request-reactivation",
    response_model=ReactivationRequestAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar reactivación de cuenta",
)
@limiter.limit("3/minute")
def request_reactivation(
    request: Request,
    data: ReactivationRequestCreate,
    service: ReactivationService = Depends(get_reactivation_service),
) -> ReactivationRequestAccepted:
    """Endpoint público para que un usuario con cuenta desactivada solicite reactivación.

    Siempre 202 con el mismo mensaje: no revela si el correo está registrado ni si
    la cuenta está activa (igual que /forgot-password).
    """
    service.request(data.email, data.reason)
    return ReactivationRequestAccepted(message=REQUEST_RECEIVED)
