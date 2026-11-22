# Frontend de BoviTrack — arquitectura por features

El frontend sigue la misma idea que el backend: un **monolito modular**. Cada dominio es una *feature* con su propia API pública, y las capas solo se usan en una dirección.

```
src/
├── main.tsx          Punto de entrada: monta <App/>.
├── app/              Raíz de composición: App (rutas y providers), el layout autenticado y
│                     las páginas que reúnen varias features (dashboard, detalle de finca).
├── features/<f>/     Un dominio por carpeta (ver "capas de features"). Expone SOLO su index.ts.
├── shared/           Piezas genéricas sin dominio: ui/, hooks/, layout/, theme/.
└── core/             Infraestructura: http/ (cliente axios con refresh de token y errores de la API).
```

| Capa | Puede importar | No puede importar |
|---|---|---|
| `app` | todo, por APIs públicas | — |
| `features/<f>` | `shared`, `core` y otras features **solo por** `@/features/<otra>` | `app`, archivos internos de otra feature, su propio `index.ts` |
| `shared` | solo librerías externas | `app`, `features`, `core` |
| `core` | solo librerías externas | `app`, `features`, `shared` |

**Cómo se escriben las importaciones:**
- Entre capas o features se usa el alias `@/` (= `src/`): `import { Pagination } from "@/shared/ui"`.
- Siempre por la API pública (el `index.ts`): `@/features/documents`, nunca `@/features/documents/components/DocumentManager`.
- Dentro de una feature se usan rutas relativas (`../api`). Una feature tiene como máximo un nivel de subcarpetas (`components/`, `pages/`, `hooks/`).

**Capas de features** (como las "capas de módulos" del backend): una feature solo usa features de niveles **inferiores**, y las del mismo nivel no se usan entre sí. Así no puede formarse un ciclo.

| Nivel | Features |
|---|---|
| consumidoras | `herd`, `documents`, `team`, `economics`, `reports`, `notifications`, `audit` |
| dominio | `health`, `inventory`, `milk_production`, `reproduction` |
| base | `livestock` |
| base | `farms` |
| base | `identity` |

Lo verifica **ESLint** (`no-restricted-imports` en `eslint.config.js`): `pnpm lint` falla y explica qué import rompe la frontera. Las reglas de cada feature se generan leyendo `src/features/`, y una feature nueva **debe** declararse en `FEATURE_LAYERS`; si no, el lint falla.

**Estructura verificada:** `src/test/architecture.test.ts` falla si vuelve a aparecer una carpeta fuera de las capas (`api/`, `components/`, `pages/`…), si una feature no tiene `index.ts` o `README.md`, o si anida más de un nivel de subcarpetas. `pnpm lint` corre con `--max-warnings 0`: también los avisos rompen el build de CI.

**Historia (Parte 4 del refactor):** 4a base y `documents`; 4b `identity` y `team`; 4c `farms`; 4d `livestock`, `health`, `inventory`, `milk_production`, `reproduction` y `herd`; 4e `economics`, `reports`, `notifications`, `audit`, las páginas públicas (en `app/pages`) y la eliminación de las carpetas heredadas.

## Conceptos de arquitectura

| Concepto | Respuesta para el frontend |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Cada feature, de **un** dominio de la pantalla: su cliente HTTP (`api.ts`), sus componentes y sus páginas. `app` compone, `shared` presenta y `core` comunica. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: todo lo de documentos (llamadas, tipos, componente) vive en `features/documents`. Antes estaba repartido entre `api/documents.ts` y `components/documents/`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Poco: quien usa una feature solo conoce su `index.ts`. Una feature puede reorganizar sus archivos internos sin que nadie más cambie. `shared` y `core` no conocen ningún dominio. |
| **Contrato** — ¿Qué garantiza? | El `index.ts` de cada feature es su contrato. `features/documents` expone solo `DocumentManager`, y lo comprueba `api.test.ts`. `core/http` garantiza el token en cada petición, renovarlo una sola vez si expira y un `Error` con el mensaje del backend (`getApiErrorMessage`). |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La página de la finca usa `<DocumentManager farmId={…}/>` sin saber de `FormData`, blobs ni rutas de la API. Una feature usa `http` sin saber de interceptores ni de `sessionStorage`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo lo que exporta cada `index.ts`. ESLint rechaza las importaciones profundas, el uso de `app` desde una feature, el dominio dentro de `shared`/`core` y las rutas `../../` que salen de una feature. |
