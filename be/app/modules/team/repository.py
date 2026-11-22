"""
Módulo: modules/team/repository.py (acceso a datos de team)
¿Qué? Las tablas propias de team: invitaciones y solicitudes de reactivación.
¿Para qué? Que los servicios no escriban SQL.
¿Impacto? Usuarios, roles y membresías NO se consultan aquí: son de identity y
          llegan por su puerto (identity.build_membership_directory).
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.team.models import FarmInvitation, ReactivationRequest

PENDING = "pending"


class Transaction:
    """Confirma la unidad de trabajo del caso de uso (todos los repositorios comparten la sesión)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, row: object) -> None:
        self._db.refresh(row)


class InvitationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def by_token(self, token: str) -> FarmInvitation | None:
        return self._db.execute(select(FarmInvitation).where(FarmInvitation.token == token)).scalar_one_or_none()

    def unused_for(self, email: str, farm_id: uuid.UUID) -> list[FarmInvitation]:
        stmt = select(FarmInvitation).where(
            FarmInvitation.email == email, FarmInvitation.farm_id == farm_id, FarmInvitation.used.is_(False)
        )
        return list(self._db.execute(stmt).scalars().all())

    def add(self, invitation: FarmInvitation) -> None:
        self._db.add(invitation)


class ReactivationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def pending_of_user(self, user_id: uuid.UUID) -> ReactivationRequest | None:
        stmt = select(ReactivationRequest).where(
            ReactivationRequest.user_id == user_id, ReactivationRequest.status == PENDING
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def pending_among(self, user_ids: Iterable[uuid.UUID]) -> list[ReactivationRequest]:
        """Solicitudes pendientes de esos usuarios, las más recientes primero."""
        ids = list(user_ids)
        if not ids:
            return []
        stmt = (
            select(ReactivationRequest)
            .where(ReactivationRequest.status == PENDING, ReactivationRequest.user_id.in_(ids))
            .order_by(ReactivationRequest.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def pending_by_id_among(self, request_id: uuid.UUID, user_ids: Iterable[uuid.UUID]) -> ReactivationRequest | None:
        ids = list(user_ids)
        if not ids:
            return None
        stmt = select(ReactivationRequest).where(
            ReactivationRequest.id == request_id,
            ReactivationRequest.status == PENDING,
            ReactivationRequest.user_id.in_(ids),
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def add(self, request: ReactivationRequest) -> None:
        self._db.add(request)
