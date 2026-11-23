#!/bin/sh
# What? Punto de entrada del contenedor del backend.
# Why?  1. Aplica las migraciones de Alembic antes de arrancar: el esquema de la
#          BD siempre queda al día en cada despliegue.
#       2. Arranca uvicorn según el entorno (ENVIRONMENT):
#          - production: sin --reload, con N workers (WEB_CONCURRENCY, por defecto 1).
#          - otro:       --reload, para desarrollo con el código montado (./be:/app).
# Impact? `set -e`: si una migración falla, el contenedor NO arranca la API con un
#         esquema viejo (antes seguía y respondía 500 en las primeras peticiones).
#         --proxy-headers + --forwarded-allow-ips: uvicorn toma la IP real del
#         cliente del encabezado X-Forwarded-For que pone nginx. Sin esto, todos
#         los usuarios llegaban con la IP de nginx y compartían el mismo límite de
#         intentos (rate limiting). El backend no se publica en producción: solo
#         nginx puede llamarlo, por eso se confía en el encabezado.
set -e

echo "Running Alembic migrations..."
alembic upgrade head

PROXY_FLAGS="--proxy-headers --forwarded-allow-ips=${FORWARDED_ALLOW_IPS:-*}"

if [ "${ENVIRONMENT:-development}" = "production" ]; then
  echo "Starting uvicorn (production, ${WEB_CONCURRENCY:-1} worker(s))..."
  # shellcheck disable=SC2086
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
    --workers "${WEB_CONCURRENCY:-1}" --no-server-header $PROXY_FLAGS
fi

echo "Starting uvicorn (development, --reload)..."
# shellcheck disable=SC2086
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload $PROXY_FLAGS
