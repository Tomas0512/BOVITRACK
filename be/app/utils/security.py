"""
Módulo: utils/security.py
Descripción: Utilidades de seguridad — hashing de contraseñas y manejo de tokens JWT.
¿Para qué? Proveer funciones reutilizables de seguridad que se usan en todo el sistema de auth:
           hashear contraseñas, verificar contraseñas, crear tokens JWT y decodificar tokens.
¿Impacto? Es la base de la seguridad del sistema. Un error aquí compromete toda la autenticación.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Contexto de hashing de contraseñas usando bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea un token JWT de acceso (access token).

    Args:
        data: Diccionario con los datos a incluir en el token (mínimo {"sub": email}).
        expires_delta: Tiempo de vida del token. Si no se especifica, usa el valor de config.

    Returns:
        Token JWT como string codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea un token JWT de refresco (refresh token).

    Args:
        data: Diccionario con los datos a incluir (mínimo {"sub": email}).
        expires_delta: Tiempo de vida. Si no se especifica, usa el valor de config.

    Returns:
        Token JWT de refresco como string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """Decodifica y verifica un token JWT.

    Returns:
        Diccionario con los datos del token (payload) si es válido, None si no lo es.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
