"""
Módulo: alembic/env.py
Descripción: Configuración del entorno de migraciones de Alembic.
¿Para qué? Conectar Alembic con los modelos SQLAlchemy para generar
           migraciones automáticas cuando cambies los modelos.
¿Impacto? Sin este archivo, Alembic no sabe qué base de datos usar
          ni qué modelos rastrear para generar migraciones.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importar Base y modelos para que Alembic los detecte
# from app.database import Base
# from app.models import *  # noqa: F401 — importar todos los modelos

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata = Base.metadata  # descomentar cuando tengas modelos
target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
