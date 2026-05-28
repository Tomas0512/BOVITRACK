#!/bin/sh
# ¿Qué?    Punto de entrada del contenedor del backend.
# ¿Para?   Ejecutar las migraciones de Alembic antes de arrancar uvicorn,
#           garantizando que el esquema de la BD esté al día en cada despliegue.
# ¿Impacto? Sin esto, la app arrancaría con tablas desactualizadas o inexistentes,
#           causando errores 500 en los primeros requests.

echo "Ejecutando migraciones de Alembic..."
alembic upgrade head

echo "Iniciando servidor uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
