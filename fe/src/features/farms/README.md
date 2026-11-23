# Feature `farms` — Fincas, lotes y potreros

Consume el módulo `farms` del backend: `/api/v1/farms` (fincas y catálogos), `/farms/{id}/land-plots` y `/farms/{id}/paddocks`.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: finca activa, pantallas y las llamadas que usan otras features. |
| `api/` | `farms.ts` (fincas y catálogos), `land_plots.ts` y `paddocks.ts`. |
| `context/FarmContext.tsx` | **Finca activa** de toda la app: la elegida (recordada en `localStorage`) si sigue existiendo; si no, la primera. |
| `components/` | Lotes (`LandPlotList`, `LandPlotFormModal`), potreros (`PaddockList`, `PaddockFormModal`) y el mapa aéreo de la finca (`MapaInteractivoFinca`, con `parcelGeometry`). |
| `pages/CreateFarmPage.tsx` | Alta de una finca. |
| `farms.test.tsx` y `components/*.test.ts(x)` | Finca activa, rutas del backend, API pública, mapa y geometría. |

Las páginas que **componen** varias features, como el detalle de finca (sus pestañas: ganado, sanidad, alimentación, documentos, empleados…) y el dashboard, no son de farms: viven en `app/pages`, que es la raíz de composición.

## Conceptos de arquitectura

| Concepto | Respuesta para `farms` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Del **lugar**: qué finca está activa, crearla y editarla, y cómo se divide (finca → lote → potrero), incluido su mapa. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Reúne lo que estaba repartido en `api/farms.ts`, `api/land_plots.ts`, `api/paddocks.ts`, `context/FarmContext.tsx`, `components/land_plots/`, `components/paddocks/` y `pages/CreateFarmPage.tsx`. Los tests del mapa ahora viven junto a sus componentes. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo usa `@/core/http`, `@/shared/*` e `identity` por su API pública. Las features que necesitan lotes o potreros (ganado, alimentación, leche) los piden con `listLandPlots`/`listPaddocks` y sus tipos, sin conocer los archivos de farms. |
| **Contrato** — ¿Qué garantiza? | Siempre hay una finca activa válida si el usuario tiene alguna: si la guardada se desactivó, cae en la primera. Si falla la carga, la app no se rompe (lista vacía). `useFarm` fuera del proveedor lanza un error claro. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | El menú, las alertas y las páginas solo usan `useFarm()`: `activeFarmId`, `activeFarm`, `setActiveFarmId`, `refreshFarms`. No saben dónde se guarda la preferencia. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Lo que exporta `index.ts`. Los formularios, el contexto en sí y las llamadas de escritura de lotes y potreros son internos (ESLint rechaza `@/features/farms/...`). |

**Código muerto eliminado (decisión del usuario):** `LandMap.tsx` (573 líneas) y `treemapLayout.ts`, con sus tests. Ninguna pantalla los usaba: `MapaInteractivoFinca` los había reemplazado.
