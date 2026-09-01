"""
Seed: Capitales municipales (catálogo DANE simplificado).

¿Qué? Inserta la capital de cada departamento en la tabla `city`,
       con su código DANE (regla verificable: <código_depto>001).
¿Para qué? Dar opciones reales al selector de ciudad/municipio del
           formulario de finca (requisito del revisor: tabla DANE).
¿Impacto? Idempotente con ON CONFLICT. Las demás municipalidades pueden
          añadirse luego desde el dataset oficial del DANE.
"""
from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "h2i3j4k5l6m7"
down_revision: Union[str, None] = "p1q2r3s4t5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Código de departamento → nombre de la capital (Colombia).
CAPITALS: dict[str, str] = {
    "05": "Medellín",
    "08": "Barranquilla",
    "11": "Bogotá D.C.",
    "13": "Cartagena",
    "15": "Tunja",
    "17": "Manizales",
    "18": "Florencia",
    "19": "Popayán",
    "20": "Valledupar",
    "23": "Montería",
    "25": "Bogotá D.C.",
    "27": "Quibdó",
    "41": "Neiva",
    "44": "Riohacha",
    "47": "Santa Marta",
    "50": "Villavicencio",
    "52": "Pasto",
    "54": "Cúcuta",
    "63": "Armenia",
    "66": "Pereira",
    "68": "Bucaramanga",
    "70": "Sincelejo",
    "73": "Ibagué",
    "76": "Cali",
    "81": "Arauca",
    "85": "Yopal",
    "86": "Mocoa",
    "88": "San Andrés",
    "91": "Leticia",
    "94": "Inírida",
    "95": "San José del Guaviare",
    "97": "Mitú",
    "99": "Puerto Carreño",
}


def upgrade() -> None:
    bind = op.get_bind()
    # Obtenemos los departamentos con su código para enlazar la capital.
    depts = bind.execute(sa.text("SELECT id, code, name FROM department")).fetchall()
    for dept_id, code, name in depts:
        capital = CAPITALS.get(code)
        if not capital:
            capital = name if "D.C." in name else f"{name} (capital)"
        dane_code = f"{code}001"
        bind.execute(
            sa.text(
                """
                INSERT INTO city (id, department_id, name, code)
                VALUES (:id, :dept_id, :name, :code)
                ON CONFLICT (department_id, name) DO UPDATE SET code = EXCLUDED.code
                """
            ),
            {"id": str(uuid.uuid4()), "dept_id": str(dept_id), "name": capital, "code": dane_code},
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM city WHERE code LIKE '%001'"))
