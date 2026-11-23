# Feature `economics` — Información económica (HU010)

Consume el módulo `economics` del backend (`/farms/{id}/economics` y `/indicators`).

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `EconomicDashboard`. |
| `api.ts` | Registros de ingresos y gastos (CRUD) e indicadores del período. |
| `pages/EconomicDashboard.tsx` | Tablero económico de la finca (`/farms/:farmId/economics`). |
| `economics.test.ts` | Rutas del backend y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `economics` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Del **dinero** de la finca: ingresos, gastos e indicadores. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Antes `api/economics.ts` y `pages/EconomicDashboard.tsx` vivían en carpetas separadas. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | No usa otras features; solo `core` y `shared`. |
| **Contrato** — ¿Qué garantiza? | Las mismas rutas del backend; el rango de fechas lo valida el backend (422). |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `app` monta `<EconomicDashboard>` en su ruta. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo la página. Es una feature consumidora: nadie depende de ella. |
