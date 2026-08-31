"""Vincula cada potrero a un lote (finca > lote > potrero).

¿Qué?     Añade paddock.land_plot_id como FK obligatoria a land_plot.
¿Para qué? La jerarquía real es finca > lote > potrero. El servicio ya exigía
           que existiera al menos un lote antes de crear un potrero, pero nunca
           guardaba a cuál pertenecía: los potreros quedaban colgando de la finca.
¿Impacto? Los potreros existentes se reasignan al lote con el que ya aparecen
          relacionados en paddock_herd; si no hay registro, al primer lote
          activo de su finca. Un potrero sin lote posible se elimina (no puede
          existir en el nuevo modelo).

Revision ID: p1q2r3s4t5u6
Revises: o1p2q3r4s5t6
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "p1q2r3s4t5u6"
down_revision = "o1p2q3r4s5t6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Columna nullable para poder rellenarla antes de exigirla.
    op.add_column(
        "paddock",
        sa.Column("land_plot_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Backfill desde el historial de ocupación, que ya relaciona ambos.
    op.execute(
        """
        UPDATE paddock p
        SET land_plot_id = sub.land_plot_id
        FROM (
            SELECT DISTINCT ON (paddock_id) paddock_id, land_plot_id
            FROM paddock_herd
            ORDER BY paddock_id, entry_date DESC
        ) AS sub
        WHERE sub.paddock_id = p.id
        """
    )

    # 3. Los que queden sueltos van al primer lote activo de su finca.
    op.execute(
        """
        UPDATE paddock p
        SET land_plot_id = sub.id
        FROM (
            SELECT DISTINCT ON (farm_id) farm_id, id
            FROM land_plot
            WHERE is_active IS TRUE
            ORDER BY farm_id, created_at ASC
        ) AS sub
        WHERE p.land_plot_id IS NULL AND sub.farm_id = p.farm_id
        """
    )

    # 4. Un potrero cuya finca no tiene ningún lote no cabe en el modelo nuevo.
    op.execute("DELETE FROM paddock_herd WHERE paddock_id IN (SELECT id FROM paddock WHERE land_plot_id IS NULL)")
    op.execute("DELETE FROM paddock WHERE land_plot_id IS NULL")

    # 5. Ya se puede exigir.
    op.alter_column("paddock", "land_plot_id", nullable=False)
    op.create_foreign_key(
        "paddock_land_plot_id_fkey", "paddock", "land_plot",
        ["land_plot_id"], ["id"], ondelete="CASCADE",
    )
    op.create_index("ix_paddock_land_plot_id", "paddock", ["land_plot_id"])


def downgrade() -> None:
    op.drop_index("ix_paddock_land_plot_id", table_name="paddock")
    op.drop_constraint("paddock_land_plot_id_fkey", "paddock", type_="foreignkey")
    op.drop_column("paddock", "land_plot_id")
