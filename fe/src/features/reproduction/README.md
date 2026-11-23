# Feature `reproduction` — Eventos reproductivos

Consume el módulo `reproduction` del backend (`/farms/{id}/reproductive-events`).

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `ReproductiveTimeline` y `listReproductiveEvents`. |
| `api.ts` | Listar, registrar y eliminar eventos (servicio, parto, aborto…). |
| `components/ReproductiveTimeline.tsx` | Línea de tiempo reproductiva de un bovino. |
| `reproduction.test.tsx` | Carga, estado vacío, error, rutas y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `reproduction` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De la **historia reproductiva** de cada animal. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: llamadas y línea de tiempo juntas. Antes estaban en `api/reproductive_events.ts` y en `components/bovines/`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | No usa ninguna otra feature: recibe `farmId` y `bovineId` por props. |
| **Contrato** — ¿Qué garantiza? | Tras registrar o eliminar un evento, la lista se recarga. Una respuesta vieja nunca pisa a una nueva. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La página del bovino usa `<ReproductiveTimeline farmId bovineId/>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo de `index.ts`. |

**Lint corregido:** el `useEffect` dependía de una función `load` sin declararla. Ahora cada recarga sube un contador y el resultado recuerda a qué carga pertenece, así que "cargando" se deriva sin llamar a `setState` dentro del efecto.
