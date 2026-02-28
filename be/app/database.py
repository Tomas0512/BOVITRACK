"""
Módulo: database.py
Descripción: Configuración de la conexión a PostgreSQL con SQLAlchemy 2.0.
¿Para qué? Proveer el engine (motor de conexión), la sesión (SessionLocal) y la
           clase base (Base) que todos los modelos ORM heredan.
¿Impacto? Este módulo es el puente entre Python y PostgreSQL. Sin él, ningún modelo
          puede crear tablas ni hacer consultas a la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# Motor de conexión — gestiona el pool de conexiones a PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Fábrica de sesiones — cada llamada a SessionLocal() crea una nueva sesión de BD.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM del proyecto.
    Cada modelo que herede de Base se convierte automáticamente en una tabla de la BD.
    """

    pass
