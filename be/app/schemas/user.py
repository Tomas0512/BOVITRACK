"""
Módulo: schemas/user.py
Descripción: Schemas Pydantic para validación de datos de entrada (request) y salida (response).
¿Para qué? Definir la "forma" exacta de los datos que la API acepta y retorna.
           Pydantic valida automáticamente tipos, formatos y restricciones — si los datos
           no cumplen el schema, FastAPI retorna un 422 con detalles del error.
¿Impacto? Sin schemas, la API aceptaría cualquier dato sin validación.
"""

import re
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ════════════════════════════════════════
# 📋 Enums
# ════════════════════════════════════════


class DocumentType(str, Enum):
    """Tipos de documento válidos — coinciden con el select del frontend."""

    CC = "CC"
    CE = "CE"
    TI = "TI"
    PP = "PP"
    NIT = "NIT"


# ════════════════════════════════════════
# 📥 Schemas de REQUEST
# ════════════════════════════════════════


class UserCreate(BaseModel):
    """Schema para el registro de un nuevo usuario.

    Campos del formulario de RegisterPage:
    firstName, lastName, documentType, documentNumber, email, phone, password.
    """

    email: EmailStr
    first_name: str
    last_name: str
    document_type: DocumentType
    document_number: str
    phone: str
    password: str
    accept_terms: bool
    accept_data_policy: bool

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Los nombres deben tener al menos 2 caracteres")
        if len(v) > 255:
            raise ValueError("Los nombres no pueden exceder 255 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", v):
            raise ValueError("Los nombres solo pueden contener letras")
        return v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Los apellidos deben tener al menos 2 caracteres")
        if len(v) > 255:
            raise ValueError("Los apellidos no pueden exceder 255 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", v):
            raise ValueError("Los apellidos solo pueden contener letras")
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
        """Valida fortaleza de contraseña — mismas reglas que el frontend."""
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


class UserLogin(BaseModel):
    """Schema para el login — email y contraseña."""

    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitar recuperación de contraseña — solo email."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema para restablecer la contraseña con un token de recuperación."""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
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


class RefreshTokenRequest(BaseModel):
    """Schema para renovar el access token usando el refresh token."""

    refresh_token: str


class DeleteAccountRequest(BaseModel):
    """Confirmación explícita para eliminar cuenta."""

    confirmation_text: str


# ════════════════════════════════════════
# 📤 Schemas de RESPONSE
# ════════════════════════════════════════


class UserResponse(BaseModel):
    """Schema de respuesta con datos del usuario (sin password)."""

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    document_type: str
    document_number: str
    phone: str
    role_name: str | None = None
    email_verified: bool = False
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema de respuesta con los tokens de autenticación."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Schema de respuesta genérico con un mensaje."""

    message: str
