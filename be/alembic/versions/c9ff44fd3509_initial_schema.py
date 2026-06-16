"""initial_schema — crea todas las tablas del sistema BoviTrack

Revision ID: c9ff44fd3509
Revises: 
Create Date: 2026-06-01 17:33:41.916603

¿Qué?    Primera migración del ciclo limpio de migraciones.
¿Para?   Crear el esquema completo de la BD desde cero usando los modelos ORM.
¿Impacto? Crea todas las tablas en el orden correcto (FK-safe) usando
          Base.metadata.create_all(). Las migraciones futuras usarán
          el enfoque incremental estándar de Alembic (op.create_table, etc.).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c9ff44fd3509'
down_revision: Union[str, None] = 'l1m2n3o4p5q6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Importar todos los modelos para que Base.metadata los conozca
    from app.database import Base  # noqa: F401
    import app.models  # noqa: F401 — registra todos los modelos en Base.metadata

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    from app.database import Base  # noqa: F401
    import app.models  # noqa: F401

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)

