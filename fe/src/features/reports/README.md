# Feature `reports` — Reportes

Consume el módulo `reports` del backend (`/farms/{id}/reports`): reportes productivo, sanitario y económico en pantalla (JSON) o descargables (PDF y Excel).

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `ReportsPage`. |
| `api.ts` | Generar el reporte (JSON o blob) y descargarlo como archivo. |
| `pages/ReportsPage.tsx` | Página de reportes (`/farms/:farmId/reports`). |
| `reports.test.ts` | JSON frente a blob, nombre del archivo y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `reports` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **resumir** la finca por categoría y período, y entregarlo como archivo. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: generar, mostrar y descargar el reporte. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | No usa otras features. Los datos ya vienen consolidados del backend (que es un modelo de lectura). |
| **Contrato** — ¿Qué garantiza? | PDF y Excel se piden como **blob**, para que el archivo no llegue corrupto, y se descargan con la extensión correcta. Una fecha inválida la rechaza el backend (422). |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `app` monta `<ReportsPage>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo la página. Es una feature consumidora. |
