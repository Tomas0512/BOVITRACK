"""Script temporal para ver las tablas y datos de la BD."""
import psycopg2

conn = psycopg2.connect("postgresql://bovitrack_user:bovitrack_pass@localhost:5432/bovitrack_db")
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
