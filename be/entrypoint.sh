#!/bin/sh
# What? Entry point for the backend container.
# Why? Run Alembic migrations before starting uvicorn,
#       ensuring the DB schema is up-to-date on every deploy.
# Impact? Without this the app would start with outdated/missing tables,
#         causing 500 errors on the first requests.

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
