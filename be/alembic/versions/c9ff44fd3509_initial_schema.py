"""initial_schema — crea la tabla `weight` (antes: create_all de todos los modelos)

Revision ID: c9ff44fd3509
Revises: l1m2n3o4p5q6
Create Date: 2026-06-01 17:33:41.916603

¿Qué?    Crea la tabla `weight` (pesajes del bovino), la única tabla que ninguna
         otra migración crea.
¿Para?   Que la cadena de migraciones sea reproducible y se pueda deshacer
         completa (`alembic downgrade base`).
¿Impacto? Antes esta migración llamaba a Base.metadata.create_all() con los
         modelos de HOY: en una BD nueva creaba de golpe `weight` y también
         `document`, `stock_movement`, `notification_log` y
         `user_notification_pref`, que son de migraciones posteriores (por eso
         esas tienen una guarda `has_table`). Y su downgrade hacía drop_all():
         borraba TODAS las tablas, incluidas las de migraciones anteriores, y la
         bajada hasta base fallaba.

         Ahora la tabla se define aquí, congelada: lo que haga esta migración ya
         no cambia cuando cambian los modelos. Las BD existentes no se ven
         afectadas (ya tienen aplicada esta revisión y la tabla `weight` es
         idéntica). Las otras cuatro tablas las crean sus propias migraciones.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = 'c9ff44fd3509'
down_revision: Union[str, None] = 'l1m2n3o4p5q6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # La guarda cubre una BD que ya tuviera `weight` (por ejemplo, creada a mano
    # con create_all antes de estampar la revisión).
    if sa.inspect(op.get_bind()).has_table("weight"):
        return

    op.create_table(
        "weight",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bovine_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weight_kg", sa.Numeric(8, 2), nullable=False),
        sa.Column("measured_at", sa.Date(), nullable=False),
        sa.Column("daily_gain", sa.Numeric(6, 2), nullable=True),
        sa.Column("body_condition", sa.Integer(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("registered_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("synchronized", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bovine_id"], ["bovine.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["registered_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Solo lo que creó esta migración. drop_table también borra sus índices y FKs.
    if sa.inspect(op.get_bind()).has_table("weight"):
        op.drop_table("weight")
