"""Permiso propio para el módulo de documentos ("documentos").

¿Qué? Crea, para cada rol, el permiso del módulo "documentos" copiando los
      valores que ese rol tiene hoy en "bovinos".
¿Para qué? Los endpoints de documentos exigían el permiso de bovinos: quien no
           tenía acceso a ganado tampoco podía gestionar los documentos de la
           finca. Con un módulo propio se pueden ajustar por separado.
¿Impacto? Nadie gana ni pierde acceso al aplicar esta migración (se copian los
          permisos de bovinos). Es idempotente (ON CONFLICT) y reversible.

Revision ID: r1s2t3u4v5w6
Revises: q1r2s3t4u5v6
"""

from typing import Sequence, Union

from alembic import op

revision: str = "r1s2t3u4v5w6"
down_revision: Union[str, None] = "q1r2s3t4u5v6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO permission (id, role_id, module, can_create, can_read, can_update, can_delete, created_at)
        SELECT gen_random_uuid(), p.role_id, 'documentos',
               p.can_create, p.can_read, p.can_update, p.can_delete, now()
        FROM permission p
        WHERE p.module = 'bovinos'
        ON CONFLICT (role_id, module) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM permission WHERE module = 'documentos'")
