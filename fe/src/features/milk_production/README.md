# Feature `milk_production` — Producción de leche

Consume el módulo `milk_production` del backend (`/farms/{id}/milk-production`).

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `MilkProductionDashboard` (pestaña de la finca), `MilkProductionList` (ordeños de un bovino) y `listMilkProduction`. |
| `api.ts` | Registros de ordeño. |
| `components/` | Tablero, lista y formulario de ordeño. |
| `milk_production.test.ts` | Rutas del backend y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `milk_production` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De los **ordeños**: registrarlos y ver la producción de la finca y de cada vaca. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Reúne `components/milk/` y el antiguo `components/bovines/MilkProductionList.tsx`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Usa `livestock` (para elegir la vaca) y `farms` (lote), por sus APIs públicas. |
| **Contrato** — ¿Qué garantiza? | Las mismas rutas del backend. Los duplicados y demás errores llegan con el mensaje del backend. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La finca y el dashboard usan `<MilkProductionDashboard>` y `listMilkProduction`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo de `index.ts`. |
