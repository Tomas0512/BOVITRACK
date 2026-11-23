"""
Módulo: modules/economics/dependencies.py (composición del módulo)
¿Qué? Arma un EconomicsService por request con su repositorio y la auditoría.
¿Para qué? Concentrar aquí el acoplamiento con lo de afuera: la auditoría (core)
           y los guards (identity).
¿Impacto? Cuando la escritura de auditoría pasó a core (Parte 3e), solo cambió este import.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.economics.repository import EconomicRecordRepository
from app.modules.economics.service import EconomicsService

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_economics_service(db: Session = Depends(get_db)) -> EconomicsService:
    """Dependencia de FastAPI: un EconomicsService por request."""
    return EconomicsService(
        repository=EconomicRecordRepository(db),
        record_audit=partial(add_audit_log, db),
    )
