"""
Módulo: core/error_handlers.py
Descripción: Traduce los errores de dominio (app.shared.exceptions) a respuestas HTTP.

¿Qué? Un único manejador registrado en la app que convierte cualquier DomainError
      en una respuesta JSON con el código de estado que le corresponde.
¿Para qué? Que la frontera HTTP sea la única capa que conoce los códigos de estado.
           Los servicios lanzan NotFoundError; el cliente recibe un 404.
¿Impacto? Si un servicio lanza una subclase nueva que no está en el mapa, se
          responde con el código de su clase padre más cercana (o 400 si es un
          DomainError genérico), nunca con un 500.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.shared.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    DomainError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
    TooManyAttemptsError,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    BusinessRuleError: status.HTTP_400_BAD_REQUEST,
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
    InvalidRequestError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    TooManyAttemptsError: status.HTTP_429_TOO_MANY_REQUESTS,
    DomainError: status.HTTP_400_BAD_REQUEST,
}


def status_for(exc: DomainError) -> int:
    """Devuelve el código HTTP de la clase más específica que esté en el mapa."""
    for cls in type(exc).__mro__:
        if cls in STATUS_BY_ERROR:
            return STATUS_BY_ERROR[cls]
    return status.HTTP_400_BAD_REQUEST


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Responde con {"detail": mensaje}, el mismo formato que HTTPException."""
    _ = request
    if not isinstance(exc, DomainError):
        raise exc
    # 401 siempre indica cómo autenticarse (RFC 7235).
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthenticationError) else None
    return JSONResponse(status_code=status_for(exc), content={"detail": exc.message}, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    """Registra el traductor de errores de dominio en la aplicación."""
    app.add_exception_handler(DomainError, domain_error_handler)
