"""
Módulo: modules/reproduction/dependencies.py (composición del módulo)
¿Qué? Arma un ReproductionService por request y conecta sus colaboradores de
      otros dominios: búsqueda de bovinos y registro de crías (ganado),
      validación de alcance (fincas) y auditoría.
¿Para qué? Que esos acoplamientos vivan solo aquí; el servicio solo conoce
           puertos (BovineLookup, CalfRegistrar, FarmScopeChecker, AuditRecorder).
¿Impacto? Todos comparten la MISMA sesión de BD: las crías y el evento se
          guardan en una sola transacción, igual que antes del refactor.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms, livestock
from app.modules.reproduction.repository import ReproductiveEventRepository
from app.modules.reproduction.service import ReproductionService

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_reproduction_service(db: Session = Depends(get_db)) -> ReproductionService:
    """Dependencia de FastAPI: un ReproductionService por request."""
    return ReproductionService(
        repository=ReproductiveEventRepository(db),
        find_bovine=livestock.build_bovine_lookup(db),
        ensure_farm_scope=farms.build_farm_scope_checker(db, find_bovine=livestock.build_bovine_lookup(db)),
        register_calf=livestock.build_calf_registrar(db),
        record_audit=partial(add_audit_log, db),
    )
