"""
Módulo: shared/exceptions.py
Descripción: Errores de dominio, independientes de HTTP y de la base de datos.

¿Qué? Jerarquía de excepciones que expresan *qué* salió mal en términos del
      negocio ("no existe", "ya existe", "viola una regla", "no tienes permiso"),
      sin decir *cómo* se responde al cliente.
¿Para qué? Que los servicios lancen errores sin importar FastAPI. Así la capa
           de negocio no conoce HTTP, y la traducción a códigos de estado ocurre
           en un solo lugar (app.core.error_handlers).
¿Impacto? Contrato de errores: todo DomainError llega al cliente como
          {"detail": "<mensaje>"}, el mismo formato que usa HTTPException, así
          que el frontend no necesita cambios.
"""


class DomainError(Exception):
    """Error base del dominio. Si se lanza directamente, se responde con 400."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """El recurso pedido no existe o no pertenece al alcance del usuario (404)."""


class ConflictError(DomainError):
    """La operación choca con el estado actual, p. ej. un duplicado (409)."""


class BusinessRuleError(DomainError):
    """Los datos son válidos en forma pero violan una regla del negocio (400)."""


class PermissionDeniedError(DomainError):
    """El usuario está autenticado pero no puede hacer esta operación (403)."""


class InvalidRequestError(DomainError):
    """La petición está bien formada pero sus valores no tienen sentido
    (p. ej. un rango de fechas invertido o en el futuro) (422)."""


class AuthenticationError(DomainError):
    """No se sabe quién hace la petición: credenciales o token inválidos (401).
    La respuesta incluye `WWW-Authenticate: Bearer`, como pide el estándar HTTP."""


class TooManyAttemptsError(DomainError):
    """Se superó el límite de intentos y hay que esperar (429)."""
