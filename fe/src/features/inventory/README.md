# Feature `inventory` — Alimentos e inventario

Consume el módulo `inventory` del backend: alimentos, compras, consumos y movimientos de stock de la finca.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `FoodList` (pestaña de alimentación), `BovineFoodList` (consumos de un bovino) y `listConsumptions`. |
| `api.ts` | Alimentos, compras, consumos y stock. |
| `components/` | Lista y formularios de alimentos, compras y consumos, tablero de inventario y `BovineFoodList`. |
| `inventory.test.ts` | Rutas del backend y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `inventory` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De los **insumos**: qué alimentos hay, cuánto se compra y cuánto se consume. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Reúne `components/food/` y el antiguo `components/bovines/FoodList.tsx`, renombrado a `BovineFoodList` porque se llamaba igual que el `FoodList` de la pestaña. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Usa `livestock` (a qué bovino se le da el alimento) y `farms` (lote y potrero), solo por sus APIs públicas. |
| **Contrato** — ¿Qué garantiza? | Las mismas rutas del backend. Los errores de stock llegan con el mensaje del backend. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La finca usa `<FoodList farmId>` y el bovino `<BovineFoodList>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo de `index.ts`. |

**Lint corregido:** `FoodUpdate` era una interfaz vacía; ahora es `type FoodUpdate = Partial<FoodCreate>`.
