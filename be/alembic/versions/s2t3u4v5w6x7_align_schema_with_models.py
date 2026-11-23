"""Alinea la BD con los modelos (Parte 5 del refactor).

¿Qué? Los dos únicos cambios de ESQUEMA que salieron de comparar los modelos con
      la BD real (`alembic check`). Las demás diferencias se resolvieron en los
      modelos, porque la BD tenía razón (índices, fechas con hora, ondelete).
      1. sanitary_plan.dose: VARCHAR(50) -> VARCHAR(100), como declara el modelo.
      2. email_verification_tokens.token: una restricción UNIQUE + un índice común
         (redundante) pasan a ser un solo índice único, igual que en
         password_reset_tokens.
¿Para qué? 1. Una dosis de 51 a 100 caracteres (p. ej. "2 mL por cada 50 kg de
              peso vivo, repetir a los 21 días") daba 500: la API la aceptaba y
              la BD la rechazaba.
           2. Un solo índice para lo mismo; el modelo y la BD quedan iguales.
¿Impacto? Ampliar un VARCHAR no reescribe datos. El índice único se puede crear
          porque la restricción ya garantizaba que no hay tokens repetidos.
          El downgrade recorta las dosis a 50 caracteres (no se puede volver a
          VARCHAR(50) sin hacerlo).

Revision ID: s2t3u4v5w6x7
Revises: r1s2t3u4v5w6
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "s2t3u4v5w6x7"
down_revision: Union[str, None] = "r1s2t3u4v5w6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("sanitary_plan", "dose", type_=sa.String(100), existing_type=sa.String(50), existing_nullable=True)

    op.drop_index("ix_email_verification_tokens_token", table_name="email_verification_tokens")
    op.drop_constraint("email_verification_tokens_token_key", "email_verification_tokens", type_="unique")
    op.create_index("ix_email_verification_tokens_token", "email_verification_tokens", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_email_verification_tokens_token", table_name="email_verification_tokens")
    op.create_unique_constraint("email_verification_tokens_token_key", "email_verification_tokens", ["token"])
    op.create_index("ix_email_verification_tokens_token", "email_verification_tokens", ["token"])

    op.execute("UPDATE sanitary_plan SET dose = left(dose, 50) WHERE length(dose) > 50")
    op.alter_column("sanitary_plan", "dose", type_=sa.String(50), existing_type=sa.String(100), existing_nullable=True)
