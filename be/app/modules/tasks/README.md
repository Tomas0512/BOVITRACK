# Módulo `tasks` — Tareas operativas

**Endpoints:** `/api/v1/farms/{farm_id}/tasks` (crear, listar con filtros, detalle, actualizar, eliminar)
**Tabla:** `task`
**Permiso:** módulo `tareas` (`can_create`, `can_read`, `can_update`, `can_delete`)

| Archivo | Capa | Responsabilidad |
|---|---|---|
| `router.py` | HTTP | Valida la entrada, exige el permiso, llama al servicio y arma `TaskResponse`. |
| `dependencies.py` | Composición | Arma `TaskService` por request y conecta los colaboradores de otros dominios. |
| `service.py` | Negocio | Casos de uso: crear, listar, consultar, actualizar y eliminar. |
| `schemas.py` | Contrato | `TaskCreate`, `TaskUpdate` y `TaskResponse`. |
| `repository.py` | Datos | Consultas SQLAlchemy sobre `task`, siempre filtradas por `farm_id`. |
| `models.py` | Persistencia | Tabla ORM `Task`. |

## Conceptos de arquitectura

| Concepto | Respuesta para `tasks` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De asignar trabajo a un miembro de la finca y seguirlo hasta cerrarlo: quién asigna, quién ejecuta, para cuándo, con qué prioridad y en qué estado está. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Todo gira alrededor de la entidad `Task`. Validar que un bovino sea de la finca **no** es de este módulo (es de `farms`), por eso llega como colaborador inyectado y no se implementa aquí. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Muy poco. Depende de 3 cosas externas: `core` (sesión de BD), identidad (`get_current_user`, `require_permission`) y dos colaboradores (alcance de finca y auditoría). Esos dos están conectados **solo** en `dependencies.py`: si sus módulos cambian, se toca ese archivo y nada más. El servicio no los importa. |
| **Contrato** — ¿Qué garantiza? | **Entrada:** `TaskCreate` exige `assigned_to`, `title`, `task_type` y `due_date`. `status` y `priority` solo aceptan sus valores válidos. **Salida:** `TaskResponse`, con quién asignó y quién ejecuta. **Errores:** tarea inexistente o de otra finca → `404 "Tarea no encontrada"`; bovino, lote o responsable de otra finca al crear o editar → `400`; sin permiso → `403`; sin sesión → `401`. El listado siempre viene ordenado por `due_date` ascendente. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Desde fuera solo se importa `app.modules.tasks`: `api_router` y los schemas. Nadie necesita saber que existe un repositorio o cómo se arma el servicio. A su vez, el servicio solo conoce las interfaces `FarmScopeChecker` y `AuditRecorder`, no sus implementaciones. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | **Entra:** JSON validado por los schemas, `farm_id`/`task_id` y el usuario autenticado. **Sale:** `TaskResponse` o un error de dominio. **No cruza:** ni la sesión de BD hacia el servicio, ni `HTTPException` fuera del router. Se verifica con import-linter (contratos *"capas de los módulos"*, *"servicios sin FastAPI ni SQLAlchemy"* y *"API pública de tasks"*). |

## Bugs corregidos

- **Editar ahora valida el alcance de finca** (antes era un IDOR). Un bovino o lote nuevo en PUT tiene que ser de la finca, igual que al crear.
- **`status` solo acepta** `pendiente`, `en_progreso` y `completada`, y **`priority`** solo `alta`, `media` y `baja`. Cualquier otro valor → `422`. Antes se aceptaba cualquier texto, y una tarea con el estado mal escrito desaparecía de la vista `v_pending_tasks`.

## Deuda conocida

- **El frontend no consume este módulo**: no existe `fe/src/api/tasks.ts`.
