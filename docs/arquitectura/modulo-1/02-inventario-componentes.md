# Fase 2 · Instrumento A: inventario de trazabilidad — BoviTrack

**Operaciones analizadas:** `GET /farms/{farm_id}/bovines` y `POST /farms/{farm_id}/bovines`  
**Versión observada:** commit base `e097f28`, rama `ultimos-cambios`, más cambios locales sin commit.

## Consulta: listar bovinos activos

| Paso | Archivo y función | Dependencia / llamada | Evidencia (líneas) |
|---|---|---|---|
| 1. Navegación de finca | `FarmDetailPage.renderTab()` | Renderiza `BovineList` en la pestaña bovinos. | `fe/src/pages/FarmDetailPage.tsx:68–71` |
| 2. Carga de interfaz | `BovineList.fetchData()` | Al montar o cambiar finca, llama a `listBovines(farmId)` y gestiona loading/error. | `fe/src/components/bovines/BovineList.tsx:324–354` |
| 3. Cliente API | `listBovines()` | `api.get(base(farmId), { params: filters })`. | `fe/src/api/bovines.ts:53–60` |
| 4. Autenticación frontend | Interceptor de `axios.ts` | Lee `access_token` de `sessionStorage` y adjunta Bearer. | `fe/src/api/axios.ts:9–18` |
| 5. Entrada HTTP | `routers/bovines.py::list_all()` | `GET`, path UUID, filtros `sex/status/purpose`, dependencia read, response model. | `be/app/routers/bovines.py:123–138` |
| 6. Sesión e identidad | `get_db()` / `get_current_user()` | Crea sesión; valida JWT, token_version, existencia y estado del usuario. | `be/app/dependencies.py:27–91` |
| 7. Autorización | `require_permission("bovinos", "can_read")` | Comprueba UserFarm activo, Role activo y Permission.can_read. | `be/app/permissions.py:30–96` |
| 8. Servicio / consulta | `bovine_service.list_bovines()` | Construye `select(Bovine)` filtrado por finca y activo, aplica filtros y orden. | `be/app/services/bovine_service.py:127–147` |
| 9. Schema de salida | `BovineResponse` | Serializa atributos de ORM a respuesta tipada. | `be/app/schemas/bovine.py:129–164` |
| 10. Persistencia | `Bovine` / SQLAlchemy / PostgreSQL | Tabla `bovine`; el servicio no modifica registros en esta operación. | `be/app/models/bovine.py:15–44`; `be/app/database.py:15–27` |

**Entrada observada:** farm UUID `82a7b0cd-7a24-4a30-bc45-d7fb68e07a86`, sin filtros.  
**Resultado observado:** `200`, 30 elementos antes de la escritura y 31 mientras el registro de prueba estuvo activo.  
**Llamadas externas/background:** ninguna participa en este flujo.

## Escritura: registrar bovino

| Paso | Archivo y función | Dependencia / llamada | Evidencia (líneas) |
|---|---|---|---|
| 1. Formulario | `BovineFormModal.validateStep()` | Validación para UX por identificación, fechas, pesos, clasificación y ubicación. | `fe/src/components/bovines/BovineFormModal.tsx:86–109, 117–137` |
| 2. Envío de UI | `BovineFormModal.handleSubmit()` | Construye payload; para alta invoca `createBovine`; muestra error o recarga. | `fe/src/components/bovines/BovineFormModal.tsx:163–188` |
| 3. Cliente API | `createBovine()` | `api.post(base(farmId), data)`. | `fe/src/api/bovines.ts:73–76` |
| 4. Entrada HTTP | `routers/bovines.py::create()` | `POST`, `BovineCreate`, dependencia can_create y respuesta `BovineResponse`. | `be/app/routers/bovines.py:33–45` |
| 5. Sesión/identidad/permisos | `get_db()`, `get_current_user()`, `require_permission()` | Misma familia de dependencias; requiere acceso y `bovinos.can_create`. | `be/app/dependencies.py:27–91`; `be/app/permissions.py:30–96` |
| 6. Schema de entrada | `BovineCreate` | Tipos, longitud, sexo, entry_type, pesos y coherencia de fechas. | `be/app/schemas/bovine.py:17–91` |
| 7. Servicio / reglas | `bovine_service.create_bovine()` | Unicidad por finca; valida padre/madre, lote, potrero y coherencia lote-potrero. | `be/app/services/bovine_service.py:45–106` |
| 8. Persistencia/transacción | `db.add`, `flush`, `commit`, `refresh`; `rollback` ante error | Inserta el bovino; la auditoría se añade antes del commit. | `be/app/services/bovine_service.py:102–124` |
| 9. Auditoría | `add_audit_log()` | Añade `AuditLog` a la misma Session, acción `create`, entidad `bovine`. | `be/app/services/audit_service.py:20–40` |
| 10. Tablas/serialización | `Bovine`, `AuditLog`, `BovineResponse` | PostgreSQL persiste entidad/log; router valida la respuesta. | `be/app/models/bovine.py:15–44`; `be/app/models/audit_log.py:11–21`; `be/app/schemas/bovine.py:129–164` |

**Entrada observada:** identificador `ARQ-F1-20261113-01`; payload y fragmento de respuesta en `04-evidencias.md`.  
**Resultado observado:** `201`, id `89750938-1bd1-4b30-bf94-23a0ad24bcc3`; posterior GET lo encontró. DELETE devolvió `204` y lo retiró de la lista activa mediante soft delete.  
**Llamadas externas/background:** ninguna; no hay proveedor externo, cola ni tarea en segundo plano en este flujo.

## Infraestructura transversal

| Componente | Participación en estas operaciones | Referencia |
|---|---|---|
| FastAPI / registro de routers | Construcción de API y montaje de router bovines. | `be/app/main.py:62–69, 115–138` |
| CORS | Orígenes/métodos/headers admitidos. | `be/app/main.py:75–99` |
| Middleware de headers | Añade headers de seguridad a la respuesta. | `be/app/main.py:102–112` |
| Rate limit | SlowAPI queda instalado en la app; los endpoints bovines inspeccionados no llevan decorador `@limiter.limit`. | `be/app/main.py:71–73`; comparar `be/app/routers/auth.py:54–67` |
| ORM / Session | Engine PostgreSQL, SessionLocal y clase base común. | `be/app/database.py:15–35` |
| Migraciones | Alembic corre antes de Uvicorn en el entrypoint. | `be/entrypoint.sh:8–12` |
| Repositorio separado | No existe `be/app/repositories/`; las consultas SQLAlchemy están en servicios para este flujo. | Verificado por recorrido del árbol `be/app/` |
