-- ══════════════════════════════════════════════════════
-- BoviTrack — Script de inicialización de PostgreSQL
-- Se ejecuta automáticamente la primera vez que el
-- contenedor de la BD arranca (directorio initdb.d).
--
-- NOTA: Las tablas las crea Alembic (migraciones del backend).
--       Aquí solo van configuraciones iniciales de la BD.
-- ══════════════════════════════════════════════════════

-- Habilitar extensión uuid-ossp para generar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Confirmar que la BD está lista
SELECT 'BoviTrack DB inicializada correctamente' AS status;
