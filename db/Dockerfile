# ── Imagen de PostgreSQL para BoviTrack ──────────────
# Basada en postgres:17 oficial.
# Copia scripts de inicialización que se ejecutan
# automáticamente la primera vez que arranca el contenedor.

FROM postgres:17

# Copiar script de inicialización al directorio especial de PostgreSQL
COPY init.sql /docker-entrypoint-initdb.d/

# Puerto por defecto de PostgreSQL
EXPOSE 5432
