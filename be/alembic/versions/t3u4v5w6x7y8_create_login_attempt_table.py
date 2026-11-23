"""create login_attempt table (bloqueo de login persistente)

Revision ID: t3u4v5w6x7y8
Revises: s2t3u4v5w6x7
Create Date: 2026-11-23

¿Qué?    Crea la tabla `login_attempt`: intentos fallidos de login por correo
         (guardado como SHA-256) y hasta cuándo está bloqueado.
¿Para?   Que el bloqueo tras 5 intentos fallidos sobreviva a reinicios y sea el
         mismo para todos los procesos de la API. Antes vivía en memoria.
¿Impacto? Tabla nueva, sin datos que migrar. Bajar esta revisión la borra: los
         bloqueos vigentes se pierden (los usuarios pueden volver a intentar).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "t3u4v5w6x7y8"
down_revision: Union[str, None] = "s2t3u4v5w6x7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "login_attempt",
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("last_failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("email_hash"),
    )
    op.create_index(op.f("ix_login_attempt_last_failed_at"), "login_attempt", ["last_failed_at"])


def downgrade() -> None:
    op.drop_table("login_attempt")
