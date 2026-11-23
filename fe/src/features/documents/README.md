# Feature `documents` — Gestión de documentos (HU012)

Feature piloto del frontend por features. Consume el módulo `documents` del backend (`/api/v1/farms/{farm_id}/documents`).

| Archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: solo `DocumentManager`. |
| `api.ts` | Cliente HTTP: listar, subir (multipart), descargar (blob) y eliminar. Usa `http` de `@/core/http`. |
| `components/DocumentManager.tsx` | Pestaña de documentos de la finca: filtros, subida, descarga y borrado. |
| `api.test.ts` | Rutas y formato de envío, y que la API pública solo expone `DocumentManager`. |

## Conceptos de arquitectura

| Concepto | Respuesta para `documents` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De mostrar y gestionar los archivos de una finca y de sus registros (bovino, evento reproductivo, tratamiento, plan sanitario). |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: tipos, llamadas y pantalla de documentos están juntos. Antes, `api/documents.ts` y `components/documents/` vivían en carpetas separadas por tipo de archivo. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo depende de `@/core/http`. Si el backend cambia una ruta de documentos, solo cambia `api.ts`. |
| **Contrato** — ¿Qué garantiza? | `<DocumentManager farmId>` funciona con solo el id de la finca. Los errores del backend llegan con su mensaje real. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `FarmDetailPage` solo importa `DocumentManager` de `@/features/documents`. No conoce `FormData`, blobs ni rutas. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo `DocumentManager`. Los tipos y funciones de `api.ts` son internos (ESLint rechaza `@/features/documents/api`). |
