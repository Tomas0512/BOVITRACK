"""
Módulo: modules/tasks/dependencies.py (composición del módulo)
¿Qué? Arma un TaskService listo para usar en cada request: le entrega su
      repositorio y conecta los colaboradores de otros dominios.
¿Para qué? Que el acoplamiento con otros dominios quede en UN solo archivo.
           El servicio solo conoce las interfaces (FarmScopeChecker,
           AuditRecorder); aquí se decide qué implementación real las cumple.
¿Impacto? El alcance de finca lo implementa farms (con el buscador de bovinos
          de livestock). Cuando eso cambió en la Parte 3e, solo cambió este
          archivo: el servicio y sus tests no se tocaron.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms, livestock
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.service import TaskService

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependencia de FastAPI: un TaskService por request, sobre la misma sesión."""
    return TaskService(
        repository=TaskRepository(db),
        ensure_farm_scope=farms.build_farm_scope_checker(db, find_bovine=livestock.build_bovine_lookup(db)),
        record_audit=partial(add_audit_log, db),
    )
