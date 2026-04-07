from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reactivation_request import ReactivationRequest
from app.models.user import User
from app.services.audit_service import add_audit_log


def request_reactivation(db: Session, email: str, reason: str | None) -> ReactivationRequest:
    stmt = select(User).where(User.email == email.lower().strip())
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correo no registrado")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cuenta ya está activa")

    # Check for existing pending request
    existing = db.execute(
        select(ReactivationRequest).where(
            ReactivationRequest.user_id == user.id,
            ReactivationRequest.status == "pending",
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una solicitud de reactivación pendiente",
        )

    req = ReactivationRequest(user_id=user.id, reason=reason)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def list_pending_requests(db: Session) -> list[dict]:
    stmt = (
        select(ReactivationRequest, User.email, User.first_name, User.last_name)
        .join(User, User.id == ReactivationRequest.user_id)
        .where(ReactivationRequest.status == "pending")
        .order_by(ReactivationRequest.created_at.desc())
    )
    rows = db.execute(stmt).all()
    result = []
    for req, email, first_name, last_name in rows:
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "reason": req.reason,
            "status": req.status,
            "created_at": req.created_at,
            "reviewed_at": req.reviewed_at,
            "user_email": email,
            "user_name": f"{first_name} {last_name}",
        })
    return result


def approve_request(db: Session, request_id, reviewer_id) -> ReactivationRequest:
    req = db.execute(
        select(ReactivationRequest).where(ReactivationRequest.id == request_id)
    ).scalar_one_or_none()

    if not req or req.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada o ya procesada")

    user = db.execute(select(User).where(User.id == req.user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    user.is_active = True
    req.status = "approved"
    req.reviewed_by = reviewer_id
    req.reviewed_at = datetime.now(timezone.utc)

    add_audit_log(
        db,
        user_id=str(reviewer_id),
        action="reactivation_approved",
        entity="user",
        entity_id=str(user.id),
    )
    db.commit()
    db.refresh(req)
    return req


def reject_request(db: Session, request_id, reviewer_id) -> ReactivationRequest:
    req = db.execute(
        select(ReactivationRequest).where(ReactivationRequest.id == request_id)
    ).scalar_one_or_none()

    if not req or req.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada o ya procesada")

    req.status = "rejected"
    req.reviewed_by = reviewer_id
    req.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req
