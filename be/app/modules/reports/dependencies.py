"""
Módulo: modules/reports/dependencies.py (composición del módulo)
¿Qué? Arma un ReportService por request sobre la sesión de BD.
¿Para qué? Mantener el mismo patrón que los demás módulos: el router recibe el
           servicio listo y nunca toca la sesión.
¿Impacto? Reportes no depende de ningún otro módulo en Python: todo lo lee por SQL.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportService

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependencia de FastAPI: un ReportService por request."""
    return ReportService(ReportRepository(db))
