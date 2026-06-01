from sqlalchemy import create_engine, text, inspect
import os

e = create_engine(os.environ["DATABASE_URL"])
with e.connect() as conn:
    tables = inspect(e).get_table_names()
    for t in sorted(tables):
        count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        status = "<<< VACIA" if count == 0 else f"{count} filas"
        print(f"{t:<35} {status}")
