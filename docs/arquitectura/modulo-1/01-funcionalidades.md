# Fase 1 · Reconocimiento de funcionalidades — BoviTrack

**Actividad:** Arquitectura de software · Parte I  
**Fecha de comprobación:** 13 de noviembre de 2026  
**Repositorio:** rama `ultimos-cambios`, commit base `e097f28`; el árbol de trabajo tenía modificaciones locales sin commit.  
**Ambiente ejecutado:** API y PostgreSQL locales en Docker; cuenta de QA, credenciales omitidas.

## Paso 1. Operaciones elegidas

| Operación | Funcionalidad | Por qué es válida |
|---|---|---|
| Consulta | Listar bovinos activos de una finca | Recupera el hato de la finca y no cambia su estado funcional. |
| Escritura | Registrar un bovino en una finca | Crea un registro persistente en `bovine` y un evento en `audit_log`. |

## Paso 2. Matriz funcional

| Elemento | Consulta | Escritura |
|---|---|---|
| Nombre | Listar bovinos activos de una finca | Registrar un bovino en una finca |
| Actor | Usuario autenticado, miembro activo y con permiso `bovinos.can_read`. Se usó la cuenta QA de `qa_e2e/config.py`; credenciales omitidas. | Usuario autenticado, miembro activo y con permiso `bovinos.can_create`. Se usó la cuenta QA; credenciales omitidas. |
| Resultado esperado / observado | Lista JSON, sin alterar los bovinos. **Observado:** `HTTP 200`, 30 elementos antes de la prueba de escritura. | Alta de bovino y respuesta `BovineResponse`. **Observado:** `HTTP 201`; apareció en la consulta y fue retirado de activos después de la limpieza. |
| Componente que recibe | `FarmDetailPage` → `BovineList` → Axios → router de bovinos. | `BovineFormModal` → Axios → router de bovinos. |
| Ruta y función inicial | `GET /api/v1/farms/{farm_id}/bovines` → `app.routers.bovines.list_all()`. | `POST /api/v1/farms/{farm_id}/bovines` → `app.routers.bovines.create()`. |
| Entrada | `farm_id` UUID en ruta; query opcional `sex`, `status`, `purpose`. La ejecución fue sin filtros. | `farm_id` UUID en ruta; body JSON. Obligatorios en schema: identificación, sexo, fechas de nacimiento/ingreso y tipo de ingreso. La interfaz además exige nombre, raza, pesos, propósito y lote o potrero para una alta nueva. |
| Salida | Lista de `BovineResponse`. **Observado:** `HTTP 200`, arreglo con 30 elementos inicialmente; 31 mientras el registro temporal estaba activo. | `BovineResponse`. **Observado:** `HTTP 201`, id `89750938-1bd1-4b30-bf94-23a0ad24bcc3`, identificación `ARQ-F1-20261113-01`, sexo `hembra`, raza `Criollo`, estado `activo`, peso actual `280.00`. |
| Tablas / fuentes consultadas | `bovine` (finca, activos, filtros y orden). Las dependencias consultan identidad, membresía `UserFarm`, rol y permiso. | `bovine` para verificar duplicidad; según referencias enviadas también progenitores, `LandPlot` y `Paddock`. Las dependencias consultan identidad y permisos. |
| Tablas / recursos modificados | Ninguno en la operación de negocio. | Inserta fila en `bovine` y evento en `audit_log`. La limpieza posterior fue soft delete: `is_active=false` y evento adicional de auditoría. |
| Reglas de negocio | Solo bovinos activos de la finca solicitada; filtros opcionales; orden descendente por fecha de creación; autorización de lectura. | Identificación única por finca; sexo `macho`/`hembra`; tipo de ingreso `nacimiento`/`compra`/`donacion`/`traspaso`; ingreso no anterior al nacimiento; pesos `>0` y `≤2500 kg`; referencias y relación lote/potrero coherentes con la finca. |
| Errores posibles / observados | `401` token inválido; `403` sin acceso/permiso; `422` UUID inválido. Sin resultados: `200` con `[]`. **Observado durante preparación:** una finca configurada en QA devolvió `403 No tienes acceso a esta finca`; se consultó la lista de fincas y se usó una accesible. | `422` datos o rangos inválidos; `409` identificación duplicada; `400` referencias o potrero/lote incoherentes; `401`/`403` autenticación/permisos. **Observado:** alta `201`; limpieza `204`. |

## Separación entre validación y reglas

- **Validación de entrada:** formato UUID, tipos de fecha/decimal, campos requeridos, longitudes y restricciones de schema Pydantic.
- **Reglas de negocio:** identificación única dentro de la finca, valores válidos de sexo y tipo de ingreso, coherencia de fechas y pertenencia de padres/lotes/potreros a la finca.
- Algunos invariantes de negocio están implementados dentro de `BovineCreate`; se distingue aquí la intención de la regla de su ubicación actual en el código.

## Referencias de código

- Consulta: `fe/src/components/bovines/BovineList.tsx:324–354`; `fe/src/api/bovines.ts:53–60`; `be/app/routers/bovines.py:123–138`; `be/app/services/bovine_service.py:127–147`.
- Escritura: `fe/src/components/bovines/BovineFormModal.tsx:86–109, 163–188`; `fe/src/api/bovines.ts:73–76`; `be/app/routers/bovines.py:33–45`; `be/app/schemas/bovine.py:17–91`; `be/app/services/bovine_service.py:45–124`.
- Autorización: `be/app/dependencies.py:27–91`; `be/app/permissions.py:30–96`.
- Persistencia: `be/app/models/bovine.py:15–44`; `be/app/models/audit_log.py:11–21`.
