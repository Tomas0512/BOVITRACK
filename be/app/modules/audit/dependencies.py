"""
Módulo: modules/audit/dependencies.py (composición del módulo)
¿Qué? Arma el AuditService de cada request y define el guard de acceso a la
      auditoría del sistema.
¿Para qué? La auditoría del sistema no tiene farm_id en la ruta, así que no
           puede usar require_permission. Se exige el permiso `usuarios:can_read`
           en AL MENOS una finca, y el servicio acota SIEMPRE los resultados a
           las fincas del usuario.
¿Impacto? Un usuario sin ese permiso recibe 403 (PermissionDeniedError).
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.shared.exceptions import PermissionDeniedError
from app.shared.ports import CurrentUser

# Guards y permisos de identity (su API pública). El router los importa desde aquí.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import has_permission_anywhere
from app.modules.identity import require_permission as require_permission

AUDIT_FORBIDDEN = "No tienes permiso para consultar la auditoría del sistema"


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependencia de FastAPI: un AuditService por request."""
    return AuditService(AuditRepository(db))


def require_audit_reader(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Autoriza la lectura de la auditoría del sistema (usuarios:can_read en alguna finca)."""
    if not has_permission_anywhere(db, current_user.id, "usuarios", "can_read"):
        raise PermissionDeniedError(AUDIT_FORBIDDEN)
    return current_user
