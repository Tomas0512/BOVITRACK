# Guia Operativa de Migraciones Alembic (BoviTrack)

Fecha: 20 de marzo de 2026

## 1. Objetivo

Esta guia explica como manejar cambios de base de datos en BoviTrack usando Alembic sin romper el proyecto.

## 2. Regla principal: cuando SI y cuando NO crear migracion

Crear migracion SI cuando cambias estructura (schema):

1. Crear o borrar tablas.
2. Agregar, quitar o renombrar columnas.
3. Cambiar tipos de datos.
4. Crear o modificar PK, FK, unique, check, indices.
5. Crear o modificar funciones, triggers o procedimientos (via SQL dentro de migracion).

No crear migracion para operaciones de datos del dia a dia:

1. INSERT de registros de negocio normales.
2. UPDATE de datos normales.
3. DELETE de datos normales.
4. Consultas SELECT.

## 3. Flujo recomendado en este proyecto (6 pasos)

### Paso 1. Levantar servicios necesarios

Desde la raiz del repo:

```powershell
docker compose up -d db be
```

### Paso 2. Crear migracion

Opcion A: autogenerada (cuando cambias modelos SQLAlchemy)

```powershell
docker compose exec -T be alembic revision --autogenerate -m "describe_cambio"
```

Opcion B: manual (cuando hay SQL especifico o conversiones complejas)

```powershell
docker compose exec -T be alembic revision -m "describe_cambio"
```

Luego editas el archivo nuevo en:

1. be/alembic/versions

### Paso 3. Revisar archivo de migracion antes de ejecutar

Checklist minimo:

1. revision y down_revision correctos.
2. upgrade crea/ajusta lo esperado.
3. downgrade revierte de forma segura.
4. Orden correcto de FK (tablas padre primero).
5. Enums y defaults compatibles con PostgreSQL.

### Paso 4. Aplicar migraciones

```powershell
docker compose exec -T be alembic upgrade head
```

### Paso 5. Verificar resultado

Revision actual:

```powershell
docker compose exec -T be alembic current -v
```

Ver tablas:

```powershell
docker compose exec -T db psql -U bovitrack_user -d bovitrack_db -c "\dt"
```

### Paso 6. Revertir si hay problema

Deshacer ultima migracion:

```powershell
docker compose exec -T be alembic downgrade -1
```

Deshacer hasta una revision concreta:

```powershell
docker compose exec -T be alembic downgrade <revision_id>
```

## 4. Convencion de nombres en versions

Los archivos no estan encriptados. El prefijo es un identificador unico de revision que Alembic usa para ordenar cambios.

Ejemplo:

1. 3a9f4b6c7d8e_create_bovitrack_domain_structure_tables.py
2. 5f1a2b3c4d5e_rename_app_user_to_user.py

Estructura interna minima de cada migracion:

1. revision: id unico de esa migracion.
2. down_revision: migracion anterior.
3. upgrade(): aplica cambios.
4. downgrade(): revierte cambios.

## 5. Estado actual en BoviTrack

Migraciones ya aplicadas en cadena:

1. eeee1c29cefa_create_users_and_password_reset_tokens_.py
2. 3a9f4b6c7d8e_create_bovitrack_domain_structure_tables.py
3. 5f1a2b3c4d5e_rename_app_user_to_user.py

## 6. Buenas practicas del equipo

1. Una tarea de schema = una migracion clara.
2. No editar migraciones antiguas ya aplicadas en equipo.
3. Siempre revisar autogenerate antes de ejecutar.
4. Probar upgrade y downgrade en desarrollo.
5. Hacer commit conjunto: modelos + migracion + ajustes de codigo.
6. En produccion, ejecutar backup antes de migrar.
