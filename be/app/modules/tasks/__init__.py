"""
Módulo tasks — API pública.

¿Qué? Lo único que el resto de la aplicación puede importar de este módulo.
¿Para qué? Ocultar cómo está construido por dentro (servicio, repositorio,
           composición). Si mañana cambia el repositorio, nadie afuera se entera.
¿Impacto? import-linter prohíbe importar directamente router, service,
          repository o dependencies desde fuera del módulo.

¿Por qué `api_router` se carga "perezosamente" (con __getattr__)?
Importar `app.modules.tasks.models` ejecuta primero este archivo. El registro de
modelos (app/models/__init__.py) lo hace mientras la app arranca, y si aquí se
importara el router de inmediato se formaría un ciclo:
models -> tasks/__init__ -> router -> dependencies -> otros módulos -> models (a medio cargar).
Cargándolo solo cuando alguien pide `api_router`, el modelo se puede registrar
sin arrastrar la capa HTTP. Lo verifica tests/test_tasks_module.py
(test_app_boots_like_uvicorn).
"""

from typing import TYPE_CHECKING, Any

from app.modules.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = ["TaskCreate", "TaskResponse", "TaskUpdate", "api_router"]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.tasks.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
