"""Script de diagnóstico para ver las tablas y datos de la BD.

La cadena de conexión se lee de la variable de entorno DATABASE_URL, igual que
en check_tables.py y que en la propia aplicación (app/config.py). Nunca se
escriben credenciales en el código: cualquiera que clone el repositorio
obtendría usuario y contraseña válidos de la base de datos.
"""

import os
import sys

import psycopg2

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    sys.exit(
        "Falta la variable de entorno DATABASE_URL.\n"
        "Ejemplo:  DATABASE_URL=postgresql://usuario:clave@localhost:5432/bovitrack_db python ver_bd.py"
    )

conn = psycopg2.connect(database_url)
cur = conn.cursor()

# Listar tablas
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
print("=== TABLAS ===")
for row in cur.fetchall():
    print(f"  - {row[0]}")

# Ver usuarios
cur.execute("SELECT id, email, first_name, last_name, document_type, document_number, phone, is_active FROM users")
cols = [d[0] for d in cur.description]
rows = cur.fetchall()
print(f"\n=== USERS ({len(rows)} registros) ===")
for r in rows:
    print(dict(zip(cols, r)))

conn.close()
