"""
Módulo: modules/team/service/invitations.py (casos de uso: invitar empleados)
¿Qué? Invitar a alguien a una finca por correo, mostrar la invitación en el
      formulario público y registrar (o vincular) a la persona invitada.
¿Para qué? Que un empleado entre a la finca con el rol que le ofrecieron, sin que
           nadie le cree la cuenta a mano.
¿Impacto? La invitación es de un solo uso y vence en 72 h. Solo un Administrador
          puede ofrecer el rol Administrador. Al crear una invitación nueva, las
          anteriores sin usar para el mismo correo y finca quedan anuladas.
"""

import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from app.modules.team.models import FarmInvitation
from app.modules.team.schemas import InvitationCreate, InvitationInfo, InvitationResponse, InvitedRegister
from app.modules.team.service.employees import ADMIN_ROLE_NAME, ROLE_NOT_FOUND
from app.shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError
from app.shared.ports import AuditRecorder

INVITATION_EXPIRE_HOURS = 72
FARM_NOT_FOUND = "Finca no encontrada"
ONLY_ADMIN_GRANTS_ADMIN = "Solo un administrador puede otorgar el rol Administrador"
ALREADY_MEMBER = "Este usuario ya está asignado a la finca"
INVITATION_NOT_FOUND = "Invitación no encontrada"
INVITATION_USED = "Esta invitación ya fue utilizada"
INVITATION_EXPIRED = "La invitación ha expirado"
DOCUMENT_TAKEN = "El número de documento ya está registrado"

# Envía el correo de invitación: (email=..., token=..., farm_name=...). Implementación: app.core.email.
SendInvitation = Callable[..., Awaitable[None]]


class InvitationDirectory(Protocol):
    """Puerto hacia identity (implementación: identity.MembershipDirectory)."""

    def get_user(self, user_id: uuid.UUID) -> Any: ...
    def user_by_email(self, email: str) -> Any: ...
    def document_taken(self, document_number: str) -> bool: ...
    def create_user(self, **fields: Any) -> Any: ...
    def get_role(self, role_id: uuid.UUID) -> Any: ...
    def member(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> Any: ...
    def add_member(self, user_id: uuid.UUID, farm_id: uuid.UUID, role_id: uuid.UUID, assigned_by: uuid.UUID | None) -> None: ...
    def role_name_in_farm(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> str | None: ...


class InvitationStore(Protocol):
    def by_token(self, token: str) -> FarmInvitation | None: ...
    def unused_for(self, email: str, farm_id: uuid.UUID) -> list[FarmInvitation]: ...
    def add(self, invitation: FarmInvitation) -> None: ...


class Transaction(Protocol):
    def flush(self) -> None: ...
    def commit(self) -> None: ...
    def refresh(self, row: object) -> None: ...


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(moment: datetime) -> datetime:
    """Fecha con zona horaria (UTC si la BD la devolvió sin zona), para compararla sin error."""
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


class InvitationService:
    def __init__(
        self,
        invitations: InvitationStore,
        directory: InvitationDirectory,
        transaction: Transaction,
        *,
        farm_name: Callable[[uuid.UUID], str | None],
        hash_password: Callable[[str], str],
        send_invitation: SendInvitation,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = invitations
        self._dir = directory
        self._tx = transaction
        self._farm_name = farm_name
        self._hash_password = hash_password
        self._send_invitation = send_invitation
        self._record_audit = record_audit

    async def invite(self, farm_id: uuid.UUID, data: InvitationCreate, invited_by: uuid.UUID) -> InvitationResponse:
        """Crea la invitación y envía el correo con el enlace de registro."""
        farm_name = self._farm_name(farm_id)
        if farm_name is None:
            raise NotFoundError(FARM_NOT_FOUND)
        role = self._dir.get_role(data.role_id)
        if not role:
            raise NotFoundError(ROLE_NOT_FOUND)
        if role.name == ADMIN_ROLE_NAME and self._dir.role_name_in_farm(invited_by, farm_id) != ADMIN_ROLE_NAME:
            raise PermissionDeniedError(ONLY_ADMIN_GRANTS_ADMIN)

        email = data.email.lower().strip()
        existing = self._dir.user_by_email(email)
        if existing and self._dir.member(farm_id, existing.id):
            raise ConflictError(ALREADY_MEMBER)

        for previous in self._repo.unused_for(email, farm_id):
            previous.used = True
        token = str(uuid.uuid4())
        invitation = FarmInvitation(farm_id=farm_id, email=email, token=token, role_id=data.role_id,
                                    invited_by=invited_by, expires_at=_now() + timedelta(hours=INVITATION_EXPIRE_HOURS))
        self._repo.add(invitation)
        self._tx.flush()  # bug #21: sin esto la auditoría guardaba entity_id="None"
        self._record_audit(user_id=str(invited_by), action="employee_invited", entity="farm_invitation",
                           entity_id=str(invitation.id),
                           details={"email": email, "farm_id": str(farm_id), "role_id": str(data.role_id)})
        self._tx.commit()
        self._tx.refresh(invitation)

        await self._send_invitation(email=email, token=token, farm_name=farm_name)
        return InvitationResponse(id=invitation.id, farm_id=invitation.farm_id, email=invitation.email,
                                  role_id=invitation.role_id, expires_at=invitation.expires_at,
                                  created_at=invitation.created_at)

    def info(self, token: str) -> InvitationInfo:
        """Datos públicos de la invitación, para el formulario de registro."""
        invitation = self._valid(token)
        inviter = self._dir.get_user(invitation.invited_by) if invitation.invited_by else None
        return InvitationInfo(
            email=invitation.email,
            farm_name=self._farm_name(invitation.farm_id) or "",
            role_name=self._dir.get_role(invitation.role_id).name,
            inviter_name=f"{inviter.first_name} {inviter.last_name}" if inviter else None,
        )

    def register_invited(self, data: InvitedRegister) -> Any:
        """Registra a la persona invitada y la vincula a la finca. Si ya tenía cuenta, solo la vincula."""
        invitation = self._valid(data.token)
        existing = self._dir.user_by_email(invitation.email)
        if existing:
            self._join(existing, invitation)
            self._record_audit(user_id=str(existing.id), farm_id=str(invitation.farm_id),
                               action="join_farm_by_invitation", entity="user", entity_id=str(existing.id),
                               details={"email": existing.email, "farm_id": str(invitation.farm_id)})
            self._tx.commit()
            self._tx.refresh(existing)
            return existing

        if self._dir.document_taken(data.document_number.strip()):
            raise BusinessRuleError(DOCUMENT_TAKEN)
        now = _now()
        user = self._dir.create_user(
            email=invitation.email,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            document_type=data.document_type.value,
            document_number=data.document_number.strip(),
            phone=data.phone.strip(),
            hashed_password=self._hash_password(data.password),
            email_verified=True,  # el correo lo verificó la propia invitación
            accepted_terms=data.accept_terms,
            accepted_data_policy=data.accept_data_policy,
            accepted_terms_at=now if data.accept_terms else None,
            accepted_data_policy_at=now if data.accept_data_policy else None,
        )
        self._join(user, invitation)
        self._record_audit(user_id=str(user.id), action="register_by_invitation", entity="user", entity_id=str(user.id),
                           details={"email": user.email, "farm_id": str(invitation.farm_id)})
        self._tx.commit()
        self._tx.refresh(user)
        return user

    # ── Reglas internas
    def _valid(self, token: str) -> FarmInvitation:
        invitation = self._repo.by_token(token)
        if not invitation:
            raise NotFoundError(INVITATION_NOT_FOUND)
        if invitation.used:
            raise BusinessRuleError(INVITATION_USED)
        if _aware(invitation.expires_at) < _now():
            raise BusinessRuleError(INVITATION_EXPIRED)
        return invitation

    def _join(self, user: Any, invitation: FarmInvitation) -> None:
        """Vincula a la finca con el rol ofrecido (si no lo estaba ya) y gasta la invitación."""
        if not self._dir.member(invitation.farm_id, user.id):
            self._dir.add_member(user.id, invitation.farm_id, invitation.role_id, invitation.invited_by)
        invitation.used = True
