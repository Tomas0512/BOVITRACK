"""
Módulo: dependencies.py
Descripción: Dependencias inyectables de FastAPI — funciones reutilizables que se
             inyectan en los endpoints usando Depends().
¿Para qué? Centralizar lógica que se repite en muchos endpoints (obtener sesión de BD,
           obtener usuario autenticado, etc.) para evitar duplicación.
¿Impacto? Sin este módulo, cada endpoint tendría que crear su propia sesión de BD
          y validar el token JWT manualmente, causando código repetido y propenso a errores.
"""

import uuid
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import decode_token

# OAuth2 scheme — extrae el token del header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Provee una sesión de base de datos para cada request.

    El patrón try/finally asegura que la conexión se devuelve al pool SIEMPRE.

    Yields:
        Session: Sesión de SQLAlchemy lista para hacer queries.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Obtiene el usuario autenticado a partir del access token JWT.

    Decodifica el token del header Authorization, extrae el user_id (sub)
    y busca al usuario en la BD.

    Raises:
        HTTPException 401: Si el token es inválido, expirado, o el usuario no existe.
        HTTPException 403: Si la cuenta del usuario está desactivada.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exception

    stmt = select(User).where(User.id == uuid.UUID(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )

    return user
