"""add paddock_id and source_bag to consumption.

¿Qué? Añade `paddock_id` (FK opcional a paddock, ON DELETE SET NULL) y
       `source_bag` (referencia de bulto/origen) a la tabla `consumption`.
¿Para qué? Permitir registrar el consumo de alimento por lote/potrero e
           indicar de qué bulto/origen se extrajo, manteniendo la coherencia
           con el stock del alimento.
¿Impacto? Retrocompatible: ambas columnas son requeridas solo en nuevos
          registros; los consumos existentes quedan sin esos datos.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "j3k4l5m6n7o8"
down_revision: Union[str, None] = "i2j3k4l5m6n7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("consumption", sa.Column("paddock_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_consumption_paddock",
        "consumption",
        "paddock",
        ["paddock_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("consumption", sa.Column("source_bag", sa.String(120), nullable=True))
    op.create_index("ix_consumption_paddock_id", "consumption", ["paddock_id"])


def downgrade() -> None:
    op.drop_index("ix_consumption_paddock_id", table_name="consumption")
    op.drop_column("consumption", "source_bag")
    op.drop_constraint("fk_consumption_paddock", "consumption", type_="foreignkey")
    op.drop_column("consumption", "paddock_id")
