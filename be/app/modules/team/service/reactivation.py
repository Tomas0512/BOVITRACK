"""
Módulo: modules/team/service/reactivation.py (casos de uso: reactivar cuentas)
¿Qué? Una persona con la cuenta desactivada pide que se la reactiven; un
      Administrador la aprueba o la rechaza.
¿Para qué? Recuperar el acceso sin intervenir la base de datos a mano.
¿Impacto? Un Administrador solo modera solicitudes de personas que fueron miembros
          (activos o no) de alguna finca donde él es Administrador activo. Una
          solicitud fuera de su alcance se responde como inexistente (404), para
          no revelar que existe.
          Pedir la reactivación es público y responde SIEMPRE lo mismo (exista o no
          el correo, esté activa o no la cuenta): así nadie puede usarlo para
          averiguar qué correos están registrados (Parte 6b, decisión del usuario).
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from app.modules.team.models import ReactivationRequest
from app.modules.team.schemas import ReactivationRequestDetail
from app.shared.exceptions import NotFoundError, PermissionDeniedError
from app.shared.ports import AuditRecorder

REQUEST_NOT_FOUND = "Solicitud no encontrada o ya procesada"
REQUEST_RECEIVED = (
    "Si existe una cuenta desactivada con ese correo, tu solicitud quedó registrada "
    "y un administrador la revisará."
)
USER_NOT_FOUND = "Usuario no encontrado"
ONLY_ADMIN_REVIEWS = "Solo un administrador puede gestionar solicitudes de reactivación"


class ReviewerDirectory(Protocol):
    """Puerto hacia identity (implementación: identity.MembershipDirectory)."""

    def get_user(self, user_id: uuid.UUID) -> Any: ...
    def user_by_email(self, email: str) -> Any: ...
    def users_by_ids(self, user_ids: Any) -> dict[uuid.UUID, Any]: ...
    def set_account_active(self, user: Any, active: bool) -> None: ...
    def administered_farm_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]: ...
    def users_ever_in_farms(self, farm_ids: Any) -> set[uuid.UUID]: ...


class ReactivationStore(Protocol):
    def pending_of_user(self, user_id: uuid.UUID) -> ReactivationRequest | None: ...
    def pending_among(self, user_ids: Any) -> list[ReactivationRequest]: ...
    def pending_by_id_among(self, request_id: uuid.UUID, user_ids: Any) -> ReactivationRequest | None: ...
    def add(self, request: ReactivationRequest) -> None: ...


class Transaction(Protocol):
    def commit(self) -> None: ...
    def refresh(self, row: object) -> None: ...


class ReactivationService:
    def __init__(self, requests: ReactivationStore, directory: ReviewerDirectory, transaction: Transaction, *,
                 record_audit: AuditRecorder) -> None:
        self._repo = requests
        self._dir = directory
        self._tx = transaction
        self._record_audit = record_audit

    def request(self, email: str, reason: str | None) -> None:
        """Pública: la persona con la cuenta desactivada deja su solicitud (una pendiente a la vez).

        No devuelve nada ni lanza errores por el correo: la solicitud se crea solo si
        la cuenta existe, está desactivada y no tiene otra pendiente; en cualquier
        otro caso no se hace nada. Quien llama responde siempre REQUEST_RECEIVED.
        """
        user = self._dir.user_by_email(email.lower().strip())
        if not user or user.is_active or self._repo.pending_of_user(user.id):
            return
        self._repo.add(ReactivationRequest(user_id=user.id, reason=reason))
        self._tx.commit()

    def ensure_reviewer(self, reviewer_id: uuid.UUID) -> None:
        """Solo un Administrador (activo, con rol activo) de alguna finca modera solicitudes."""
        if not self._dir.administered_farm_ids(reviewer_id):
            raise PermissionDeniedError(ONLY_ADMIN_REVIEWS)

    def list_pending(self, reviewer_id: uuid.UUID) -> list[ReactivationRequestDetail]:
        requests = self._repo.pending_among(self._scope(reviewer_id))
        users = self._dir.users_by_ids({r.user_id for r in requests})
        return [
            ReactivationRequestDetail(
                id=r.id, user_id=r.user_id, reason=r.reason, status=r.status, created_at=r.created_at,
                reviewed_at=r.reviewed_at, user_email=users[r.user_id].email,
                user_name=f"{users[r.user_id].first_name} {users[r.user_id].last_name}",
            )
            for r in requests
            if r.user_id in users
        ]

    def approve(self, request_id: uuid.UUID, reviewer_id: uuid.UUID) -> ReactivationRequest:
        request = self._pending_in_scope(request_id, reviewer_id)
        user = self._dir.get_user(request.user_id)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        self._dir.set_account_active(user, True)
        self._close(request, "approved", reviewer_id)
        self._record_audit(user_id=str(reviewer_id), action="reactivation_approved", entity="user", entity_id=str(user.id))
        self._tx.commit()
        self._tx.refresh(request)
        return request

    def reject(self, request_id: uuid.UUID, reviewer_id: uuid.UUID) -> ReactivationRequest:
        request = self._pending_in_scope(request_id, reviewer_id)
        self._close(request, "rejected", reviewer_id)
        self._tx.commit()
        self._tx.refresh(request)
        return request

    # ── Reglas internas
    def _scope(self, reviewer_id: uuid.UUID) -> set[uuid.UUID]:
        """Personas que fueron miembros (activos o no) de alguna finca que el revisor administra."""
        return self._dir.users_ever_in_farms(self._dir.administered_farm_ids(reviewer_id))

    def _pending_in_scope(self, request_id: uuid.UUID, reviewer_id: uuid.UUID) -> ReactivationRequest:
        request = self._repo.pending_by_id_among(request_id, self._scope(reviewer_id))
        if request is None:
            raise NotFoundError(REQUEST_NOT_FOUND)
        return request

    @staticmethod
    def _close(request: ReactivationRequest, status: str, reviewer_id: uuid.UUID) -> None:
        request.status = status
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now(timezone.utc)
