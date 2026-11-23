"""
Módulo: modules/milk_production/dependencies.py (composición del módulo)
¿Qué? Arma un MilkProductionService por request y conecta sus colaboradores
      de otros dominios: búsqueda de bovinos (ganado), de lotes (fincas) y la
      auditoría.
¿Para qué? Que esos acoplamientos vivan solo aquí; el servicio solo conoce los
           puertos de app.shared.ports.
¿Impacto? Cuando ganado, fincas y auditoría migren (Partes 3d y 3e), solo
          cambian estos imports.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms, livestock
from app.modules.milk_production.repository import MilkProductionRepository
from app.modules.milk_production.service import MilkProductionService

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_milk_production_service(db: Session = Depends(get_db)) -> MilkProductionService:
    """Dependencia de FastAPI: un MilkProductionService por request."""
    return MilkProductionService(
        repository=MilkProductionRepository(db),
        find_bovine=livestock.build_bovine_lookup(db),
        land_plot_exists=farms.build_land_plot_lookup(db),
        record_audit=partial(add_audit_log, db),
    )
