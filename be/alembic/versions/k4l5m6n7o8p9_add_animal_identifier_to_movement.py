"""add animal_identifier to animal_movement.

¿Qué? Añade `animal_identifier` (cadena opcional) a `animal_movement`.
¿Para qué? Permitir registrar el identificador del animal cuando se registra
           un movimiento de tipo compra/nacimiento (animal nuevo, aún no
           registrado como bovino), sin exigir un `bovine_id` existente.
¿Impacto? Retrocompatible: la columna es nullable; los movimientos existentes
          no se ven afectados.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "k4l5m6n7o8p9"
down_revision: Union[str, None] = "j3k4l5m6n7o8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("animal_movement", sa.Column("animal_identifier", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("animal_movement", "animal_identifier")
