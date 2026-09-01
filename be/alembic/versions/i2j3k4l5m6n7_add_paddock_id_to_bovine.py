"""add paddock_id to bovine.

¿Qué? Añade la columna `paddock_id` a la tabla `bovine` (FK opcional a
       paddock, ON DELETE SET NULL).
¿Para qué? Permitir asignar a cada bovino el potrero donde se encuentra,
           y así listar los animales de cada potrero (requisito del
           revisor sobre la relación animal↔potrero).
¿Impacto? Retrocompatible: el campo es nullable, los bovinos existentes
          quedan sin potrero asignado.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "i2j3k4l5m6n7"
down_revision: Union[str, None] = "h2i3j4k5l6m7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bovine",
        sa.Column("paddock_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_bovine_paddock",
        "bovine",
        "paddock",
        ["paddock_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_bovine_paddock_id", "bovine", ["paddock_id"])


def downgrade() -> None:
    op.drop_index("ix_bovine_paddock_id", table_name="bovine")
    op.drop_constraint("fk_bovine_paddock", "bovine", type_="foreignkey")
    op.drop_column("bovine", "paddock_id")
