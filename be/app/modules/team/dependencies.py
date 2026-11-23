"""
Módulo: modules/team/dependencies.py (composición del módulo)
¿Qué? Arma por request los servicios de empleados, invitaciones y reactivación, y
      el guard de los moderadores de reactivación.
¿Para qué? Es el ÚNICO archivo de team que conoce a otros módulos:
           - identity: usuarios, roles y membresías (build_membership_directory),
             el hash de contraseñas, los guards y UserResponse.
           - farms: el nombre de la finca para el correo de invitación.
¿Impacto? team está en el nivel de los consumidores: nadie depende de él.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.audit_trail import add_audit_log
from app.core.database import get_db
from app.core.email import send_farm_invitation_email
from app.modules import farms, identity
from app.modules.team.repository import InvitationRepository, ReactivationRepository, Transaction
from app.modules.team.service import EmployeeService, InvitationService, ReactivationService
from app.shared.ports import CurrentUser

# API pública de identity que usan los routers de este módulo (guards y la
# respuesta de usuario del registro por invitación).
from app.modules.identity import UserResponse as UserResponse
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(identity.build_membership_directory(db), Transaction(db), record_audit=partial(add_audit_log, db))


def get_invitation_service(db: Session = Depends(get_db)) -> InvitationService:
    return InvitationService(
        InvitationRepository(db),
        identity.build_membership_directory(db),
        Transaction(db),
        farm_name=farms.build_farm_name_lookup(db),
        hash_password=identity.build_password_hasher(),
        send_invitation=send_farm_invitation_email,
        record_audit=partial(add_audit_log, db),
    )


def get_reactivation_service(db: Session = Depends(get_db)) -> ReactivationService:
    return ReactivationService(
        ReactivationRepository(db),
        identity.build_membership_directory(db),
        Transaction(db),
        record_audit=partial(add_audit_log, db),
    )


def require_admin_role(
    service: ReactivationService = Depends(get_reactivation_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Guard: solo un Administrador (activo, con rol activo) de alguna finca modera reactivaciones (403)."""
    service.ensure_reviewer(current_user.id)
    return current_user
