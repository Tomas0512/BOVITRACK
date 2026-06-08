"""
Seed: Propósitos de finca (ganadería).
Uso: docker compose exec be python seed_purposes.py
"""
import uuid
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

PURPOSES = [
    ("Cría",        "Producción y comercialización de terneros y novillas"),
    ("Levante",     "Crecimiento y desarrollo de bovinos jóvenes"),
    ("Ceba",        "Engorde de bovinos para sacrificio"),
    ("Lechería",    "Producción de leche para consumo o industrialización"),
    ("Doble propósito", "Producción simultánea de leche y carne"),
    ("Ciclo completo",  "Cría, levante y ceba en la misma finca"),
    ("Reproducción",    "Producción de pie de cría y mejoramiento genético"),
]


def seed():
    with Session(engine) as session:
        existing = session.execute(text("SELECT COUNT(*) FROM purpose")).scalar()
        if existing and existing > 0:
            print(f"Ya existen {existing} propósitos. Nada que hacer.")
            return

        for name, description in PURPOSES:
            session.execute(
                text("INSERT INTO purpose (id, name, description) VALUES (:id, :name, :desc)"),
                {"id": str(uuid.uuid4()), "name": name, "desc": description},
            )

        session.commit()
        print(f"Seed completado: {len(PURPOSES)} propósitos insertados.")


if __name__ == "__main__":
    seed()
