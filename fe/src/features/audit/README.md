# Feature `audit` — Auditoría (HU015)

Consume el módulo `audit` del backend: `/admin/audit-logs` (auditoría del sistema, con filtros, catálogo y exportación) y `/farms/{id}/audit-logs`.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `AuditPage` (auditoría global, solo Administrador) y `AuditLogList` (pestaña de la finca). |
| `api.ts` | Auditoría por finca, búsqueda filtrada y paginada, catálogo de acciones y entidades, y descarga en CSV o Excel. |
| `components/AuditLogList.tsx` | Últimos cambios de una finca. |
| `pages/AuditPage.tsx` | Auditoría global con filtros y exportación (`/audit`). |
| `audit.test.ts` | Rutas del backend, descarga como archivo y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `audit` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **mostrar quién hizo qué**, cuándo y en qué finca, y de exportarlo como evidencia. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: consultar y exportar el rastro. Escribir la auditoría no es del frontend: lo hace el backend en cada acción. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo usa `farms` (la lista de fincas para el filtro), por su API pública. |
| **Contrato** — ¿Qué garantiza? | El usuario solo ve auditoría de sus fincas (lo garantiza el backend). La exportación se pide como **blob**, se guarda con la fecha en el nombre y libera la memoria del navegador. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `app` monta `<AuditPage>` dentro de `RequireRole role="Administrador"`; la página de la finca usa `<AuditLogList farmId>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo los dos componentes de `index.ts`. Es una feature consumidora. |
