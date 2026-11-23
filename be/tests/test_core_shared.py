"""
Pruebas de la Parte 1 del refactor: capas core y shared.

¿Qué? Verifica el contrato de errores de dominio (qué código HTTP y qué cuerpo
      recibe el cliente) y que get_db siga disponible en su ruta anterior.
¿Para qué? Garantizar que mover la infraestructura a app.core no cambió el
           comportamiento y que el nuevo traductor de errores cumple su contrato.
¿Impacto? Si alguien cambia el mapa de códigos o el formato {"detail": ...},
          estas pruebas fallan antes de que el frontend lo note.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.error_handlers import register_error_handlers, status_for
from app.shared.exceptions import (
    BusinessRuleError,
    ConflictError,
    DomainError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
)


class _CustomNotFound(NotFoundError):
    """Subclase que no está en el mapa: debe heredar el código de su padre."""


def _client_raising(exc: Exception) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise exc

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("exc", "expected_status"),
    [
        (NotFoundError("No existe"), 404),
        (ConflictError("Ya existe"), 409),
        (BusinessRuleError("Regla violada"), 400),
        (PermissionDeniedError("Sin permiso"), 403),
        (InvalidRequestError("Rango inválido"), 422),
        (DomainError("Genérico"), 400),
        (_CustomNotFound("Subclase"), 404),
    ],
)
def test_domain_errors_map_to_http_status_and_detail(exc: DomainError, expected_status: int) -> None:
    response = _client_raising(exc).get("/boom")

    assert response.status_code == expected_status
    assert response.json() == {"detail": exc.message}


def test_status_for_uses_closest_parent_class() -> None:
    assert status_for(_CustomNotFound("x")) == 404


def test_non_domain_errors_are_not_swallowed() -> None:
    response = _client_raising(RuntimeError("bug real")).get("/boom")

    assert response.status_code == 500


def test_main_app_registers_domain_error_handler() -> None:
    from app.main import app

    assert DomainError in app.exception_handlers


def test_old_guard_modules_are_gone_get_db_lives_in_core() -> None:
    # 3e-2: app/dependencies.py y app/permissions.py se borraron. get_db vive en
    # core y los guards en la API pública de identity.
    import importlib

    from app.core.database import get_db  # noqa: F401
    from app.modules.identity import get_current_user, require_permission  # noqa: F401

    for old in ("app.dependencies", "app.permissions"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(old)
