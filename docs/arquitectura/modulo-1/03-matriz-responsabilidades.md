# Fase 2 · Matriz de separación de responsabilidades — BoviTrack

**Funcionalidades:** consultar bovinos activos y registrar bovino.  
**Criterio:** se clasifica el comportamiento observado; que una responsabilidad no tenga clase/carpeta propia no se considera automáticamente un defecto.

| Componente | Archivo / función real | Responsabilidad efectiva | Evaluación |
|---|---|---|---|
| Interfaz | `FarmDetailPage.tsx`, `BovineList.tsx`, `BovineFormModal.tsx` | Presenta la pestaña, carga la lista, recoge datos y comunica validaciones/errores. La UI exige nombre, raza, pesos, propósito y lote/potrero en alta aunque algunos son opcionales en `BovineCreate`. | **Mezclada (parcial):** además de UX, impone un contrato más restrictivo que el API. Las validaciones críticas sí se repiten en backend; la diferencia de obligatoriedad puede sorprender a otros clientes. Referencias: `BovineFormModal.tsx:86–109, 117–137`; `BovineCreate:25–42`. |
| Router / entrada HTTP | `be/app/routers/bovines.py::list_all`, `create` | Enlaza método/ruta, schemas, dependencias, llamada de servicio, response model y códigos HTTP. | **Correcta:** los handlers son adaptadores HTTP delgados; no realizan la consulta o creación de bovino directamente. Referencias: líneas 33–45 y 123–138. |
| Middleware | `be/app/main.py::add_security_headers`, `CORSMiddleware`; SlowAPI | Aplica controles transversales: CORS, headers, manejo del rate limiter. | **Correcta:** no contiene reglas funcionales del hato. El rate limiter está configurado, pero no se observó decorador de límite en los dos endpoints analizados. Referencias: `main.py:71–112`. |
| Controller | No hay clase/controller independiente; `list_all()` y `create()` cumplen ese rol en las rutas FastAPI. | Adapta HTTP a llamada de aplicación y adapta resultados a respuesta. | **No aplica como componente separado:** FastAPI permite que el handler de `@router.get/post` actúe también como controller. Separarlo solo por nombre no aportaría valor demostrado aquí. |
| Service / Use Case | `be/app/services/bovine_service.py::list_bovines`, `create_bovine` | Coordina filtros, reglas de unicidad/alcance de finca, lecturas/escrituras, transacción y auditoría. | **Mezclada (parcial):** además de orquestar reglas, ejecuta `select`, usa `Session`, `add/flush/commit` directamente. Service y acceso a datos están acoplados. Para el tamaño y patrón existente puede ser pragmático; la guía pide reconocerlo, no refactorizar ahora. |
| Domain | No hay paquete `domain` ni entidad de dominio separada. Reglas repartidas en `BovineCreate`, `bovine_service` y restricciones ORM/BD. | Representa invariantes: sexo/entry_type, fechas, identificación única por finca y coherencia de referencias. | **No aplica como capa independiente:** las reglas sí existen, pero se ubican en schemas, servicio y base; el modelo `Bovine` es principalmente ORM. No es por sí solo un defecto en un monolito de este tamaño. |
| Repository / Adapter | No hay carpeta/clase repositorio dedicada. SQLAlchemy `Session`, modelos y consultas en `bovine_service.py`. | Traduce la operación a consultas ORM y persistencia PostgreSQL. | **No aplica como repositorio separado:** el adaptador sí existe vía SQLAlchemy, pero lo utiliza directamente el servicio. La consecuencia observada está recogida en la evaluación del Service; una capa extra requeriría beneficio de pruebas/reutilización. |
| Base de datos | PostgreSQL; tabla `bovine`, `audit_log`, tablas de acceso. Modelo `Bovine`. | Persiste entidades y eventos, relaciones/FKs e invariantes declarados, incluyendo unicidad compuesta `(farm_id, identification_number)`. | **Correcta:** aplica persistencia y restricciones; el código de aplicación conserva reglas de autorización y flujo. Referencia: `be/app/models/bovine.py:15–44`. |

## Justificación de calificaciones distintas de “Correcta”

1. **Interfaz — Mezclada parcial:** la UI requiere datos que la API acepta como opcionales. Es una diferencia comprobable entre `BovineFormModal.validateStep()` y `BovineCreate`, no evidencia de que deba eliminarse la validación de UX.
2. **Service — Mezclada parcial:** la misma función contiene regla de negocio y comandos ORM/transaccionales. La separación podría mejorar sustitución del almacenamiento o pruebas aisladas, pero el servicio actual está cohesionado alrededor del caso de uso bovino.
3. **Domain — No aplica independiente:** las reglas están implementadas, pero distribuidas. La actividad no exige crear carpetas por cada categoría; se registra la distribución como arquitectura actual.
4. **Repository — No aplica independiente:** SQLAlchemy es el adaptador y `Session` se inyecta; no existe una abstracción repository separada. No se infiere que sea incorrecto sin valorar escala y pruebas.

## Aplicación del ejercicio guiado

| Fragmento ilustrativo | Responsabilidad | Correspondencia observada en BoviTrack |
|---|---|---|
| Decorador y HTTPException | Adaptación HTTP / Controller. | `@router.post` y `HTTPException` en `routers/bovines.py`; el handler adapta request/response y dependencias. |
| `datos.get("titulo")` | Validación de entrada/contrato. | `BovineCreate` valida tipos, longitudes y campos; la UI tiene validaciones adicionales de experiencia de usuario. |
| `db.query(...)` | Lectura de persistencia; candidato a repository/adaptador. | `bovine_service` ejecuta `db.execute(select(...))` para duplicados, relaciones y listados. |
| `if existe` | Regla de negocio de unicidad. | `create_bovine` busca `farm_id + identification_number` y produce `409`; existe además unique constraint en ORM. |
| `estado="pendiente"` | Política de dominio / estado inicial. | `BovineCreate.status` tiene default `"activo"`; el modelo inicializa `is_active=True`. La regla queda en schema/ORM, no en un domain object independiente. |
| `db.add()` y `commit()` | Persistencia y transacción. | `create_bovine`: `add`, `flush`, añade auditoría y `commit`; ante excepción ejecuta `rollback`. |

**Resultado de la revisión:** se completó el inventario y clasificación de la arquitectura existente. Esta entrega documenta la línea base; no incluye una propuesta objetivo ni cambios/refactorización de código.
