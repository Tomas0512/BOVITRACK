# Feature `herd` — Ficha consolidada del hato

Es la pestaña **Ganado**: una tabla de todos los bovinos de la finca, con columnas configurables y filtros avanzados. Por cada animal suma datos de **cinco dominios**: producción de leche, consumos, tratamientos, movimientos y eventos reproductivos.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: solo `BovineList`. |
| `components/BovineList.tsx` | Carga los datos, los cruza por bovino y muestra la tabla (importar CSV, eliminar, seleccionar). |
| `components/bovineColumns.ts` | Columnas, filtros y cálculos (edad, formatos). |
| `components/AdvancedFiltersPanel.tsx`, `ColumnCustomizePanel.tsx` | Filtros avanzados y elección de columnas. |
| `herd.test.ts` | Cálculo y formato de la edad, y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `herd` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **ver el hato completo**: una vista de lectura que reúne lo que otros dominios saben de cada animal. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: consolidar y filtrar. No registra leche, tratamientos ni eventos; eso lo hacen sus features. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Es una feature **consumidora**, como `reports` en el backend: usa livestock, health, inventory, milk_production y reproduction, solo por sus APIs públicas, y nadie depende de ella. Antes vivía dentro de `components/bovines/` y hacía que "ganado" dependiera de cuatro dominios que a su vez dependían de él: un **ciclo**. |
| **Contrato** — ¿Qué garantiza? | Si falla la carga de un dominio secundario (por ejemplo, leche), la tabla se muestra igual, con esas columnas vacías. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La página de la finca usa `<BovineList farmId>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo `BovineList`. ESLint (capas de features) impide que una feature de nivel inferior importe `herd`. |
