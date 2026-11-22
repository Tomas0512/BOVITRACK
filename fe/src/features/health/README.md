# Feature `health` — Tratamientos y planes sanitarios

Consume el módulo `health` del backend: `/farms/{id}/treatments` y `/farms/{id}/sanitary-plans`.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `FarmTreatments`, `TreatmentList`, `SanitaryPlanList` y `listTreatments`. |
| `api/` | `treatments.ts` y `sanitary_plans.ts`. |
| `components/` | Tratamientos de la finca y de un bovino, y planes sanitarios. |
| `health.test.ts` | Rutas del backend y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `health` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De la **sanidad** del hato: tratamientos aplicados y planes sanitarios programados. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Antes sus pantallas estaban mezcladas en `components/bovines/`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo usa `livestock` (para elegir el bovino), por su API pública. |
| **Contrato** — ¿Qué garantiza? | Las mismas rutas del backend, con el filtro opcional por bovino. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La página de la finca usa `<FarmTreatments farmId>`, la del bovino `<TreatmentList>`, y herd usa `listTreatments`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo de `index.ts`. Está en el mismo nivel que inventory, milk_production y reproduction, que no se usan entre sí. |
