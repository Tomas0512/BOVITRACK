"""
Módulo: schemas/invitation.py
Schemas Pydantic para el flujo de invitación de empleados a fincas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    """Datos para crear una invitación: email del empleado y rol."""
    email: EmailStr
    role_id: uuid.UUID


class InvitationResponse(BaseModel):
    """Respuesta tras crear una invitación."""
    id: uuid.UUID
    farm_id: uuid.UUID
    email: str
    role_id: uuid.UUID
    expires_at: datetime
    created_at: datetime


class InvitationInfo(BaseModel):
    """Info pública de una invitación (para el formulario de registro)."""
    email: str
    farm_name: str
    role_name: str
    inviter_name: str | None = None


class InvitedRegister(BaseModel):
    """Datos para completar el registro como empleado invitado."""
    token: str
    first_name: str
    last_name: str
    document_type: str
    document_number: str
    phone: str
    password: str
    accept_terms: bool
    accept_data_policy: bool
