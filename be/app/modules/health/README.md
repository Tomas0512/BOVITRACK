# Módulo `health` — Sanidad del hato

**Endpoints:**
- `/api/v1/farms/{farm_id}/treatments`: crear, listar, detalle y eliminar. Permiso `tratamientos`.
- `/api/v1/farms/{farm_id}/sanitary-plans`: CRUD y `POST /{id}/apply`. Permiso `sanitario`.

**Tablas:** `treatment` (aplicaciones realizadas) y `sanitary_plan` (protocolos programados).
**Lo usa otro módulo:** `notifications` (planes vencidos y próximos).

| Archivo | Responsabilidad |
|---|---|
| `router.py` | Dos `APIRouter` (tratamientos y planes) unidos en un único `router` del módulo. |
| `dependencies.py` | Arma ambos servicios y ofrece `build_sanitary_alerts` a otros módulos. |
| `service.py` | `TreatmentService` y `SanitaryPlanService`. |
| `repository.py` | `TreatmentRepository` y `SanitaryPlanRepository`. |
| `models/`, `schemas/` | Un archivo por agregado (`treatment.py`, `sanitary_plan.py`). |

## Conceptos de arquitectura

| Concepto | Respuesta para `health` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De registrar qué se aplicó a cada animal o lote (tratamientos) y de planificar qué falta aplicar (planes con frecuencia y próxima fecha), para que ninguna vacuna se pase de fecha. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: la sanidad del hato. Son dos agregados distintos (lo hecho y lo programado), pero cambian por las mismas razones y comparten reglas, así que conviven en un módulo con una clase por agregado. Qué es un "plan vencido" se define aquí y notificaciones lo consume. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Depende de **inventario** (¿el alimento es de la finca?), solo por su API pública y solo desde `dependencies.py`. En las capas de módulos, salud está **debajo** de notificaciones y **encima** de inventario, así que import-linter impide cualquier ciclo. Bovinos (livestock), lotes y alcance de finca (farms) llegan por puertos de sus módulos; la auditoría, por `core`. |
| **Contrato** — ¿Qué garantiza? | **Tratamientos:** bovino, lote y alimento deben ser de la finca; si no, `400` con el mensaje de cada caso. Inexistente → `404 "Tratamiento no encontrado"`. Eliminar es un borrado físico. **Planes:** bovino y lote de la finca, revalidados al editar con los valores finales. `apply` registra la aplicación de hoy y programa la próxima para hoy + `frequency_days`. Desactivar es un borrado lógico (el plan deja de alertar). Inexistente → `404 "Plan sanitario no encontrado"`. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Notificaciones recibe un objeto con `overdue(farm, now)` y `upcoming(farm, now, until)` que devuelve `SanitaryDue`. No conoce la tabla ni el modelo `SanitaryPlan`. La hora de `apply` se inyecta (`now`) para probarla con una fecha fija. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Salen DTOs inmutables (`SanitaryDue`). Hacia inventario sale `(farm_id, food_id)` y vuelve un booleano. Ningún modelo ORM cruza entre módulos. |

## Deuda conocida

- `create_sanitary_plan` usa `created_by=user_id or uuid.uuid4()`. Si no hubiera usuario, inventaría un id que no existe y la FK fallaría. Hoy el router siempre pasa el usuario, así que no ocurre.
- En el modelo, `next_scheduled_date` y `last_applied_date` son `Date`, pero en la BD son `TIMESTAMP` (es parte de las 60 diferencias entre modelo y BD que se corrigen en la Parte 5).
- Los tratamientos no tienen endpoint de edición.
