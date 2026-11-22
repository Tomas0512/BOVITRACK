# Feature `livestock` — Bovinos, pesajes, terneros y movimientos

Consume el módulo `livestock` del backend: `/farms/{id}/bovines`, `…/weights`, `/farms/{id}/calves` y `/farms/{id}/movements`.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: formulario de bovino, gráfico e historial de pesos, terneros, movimientos y las llamadas que usan otras features. |
| `api/` | `bovines.ts`, `weights.ts`, `calves.ts` y `movements.ts`. |
| `components/` | `BovineFormModal`, `WeightChart`, `WeightHistory`, `CalfList`, `GrowthChart`, `MovementList`, `MovementFormModal`. |
| `livestock.test.tsx` | Carga por bovino sin carreras, errores de terneros y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `livestock` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Del **animal**: registrarlo, pesarlo y seguir a los terneros y sus movimientos. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Reúne `api/bovines|weights|calves|movements` y lo que estaba en `components/bovines`, `components/calves` y `components/movements`. La ficha consolidada del hato **no** está aquí (ver `herd`): mezcla datos de cinco dominios. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Es una feature **base**: solo usa `farms` (lotes y potreros) y `core`/`shared`. La usan health, inventory, milk_production y herd. |
| **Contrato** — ¿Qué garantiza? | Al cambiar de bovino, la respuesta tardía del anterior **no** pisa los datos del nuevo (`WeightChart`). Los errores de terneros llegan con el mensaje del backend o uno claro según el código. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Otra feature pide `listBovines(farmId)` o usa `<BovineFormModal>`, sin conocer rutas ni tipos internos. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo que exporta `index.ts`. ESLint impide que livestock importe features de niveles superiores (health, inventory, milk_production, reproduction, herd…). |

**Lint corregido:** `WeightChart` llamaba a `setState` al inicio del efecto, lo que causaba renders en cascada y podía mostrar datos de otro bovino. En `api/calves.ts` había `any`; ahora usa `Record<string, unknown>` y `unknown` con `axios.isAxiosError`.
