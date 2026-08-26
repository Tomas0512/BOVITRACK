"""
Módulo: schemas/invitation.py
Schemas Pydantic para el flujo de invitación de empleados a fincas.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.schemas.user import DocumentType


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
    document_type: DocumentType
    document_number: str
    phone: str
    password: str
    confirm_password: str
    accept_terms: bool
    accept_data_policy: bool

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "InvitedRegister":
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        if len(v) > 255:
            raise ValueError("El nombre no puede exceder 255 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", v):
            raise ValueError("El nombre solo puede contener letras")
        return v

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El número de documento es obligatorio")
        if len(v) > 50:
            raise ValueError("El número de documento no puede exceder 50 caracteres")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El teléfono es obligatorio")
        if len(v) > 20:
            raise ValueError("El teléfono no puede exceder 20 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

    @field_validator("accept_terms")
    @classmethod
    def validate_accept_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debe aceptar términos y condiciones")
        return v

    @field_validator("accept_data_policy")
    @classmethod
    def validate_accept_data_policy(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debe autorizar tratamiento de datos")
        return v
