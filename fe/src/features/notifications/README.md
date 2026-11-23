# Feature `notifications` — Alertas y notificaciones (HU014)

Consume el módulo `notifications` del backend: alertas de la finca, preferencias e historial de notificaciones.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `NotificationBell` (encabezado) y `AlertasPage`. |
| `api.ts` | Alertas próximas, preferencias, historial, contador de no leídas y marcar como leída. |
| `components/` | `NotificationBell` (campana con contador y lista) y `AlertBanner` (resumen de alertas). |
| `pages/AlertasPage.tsx` | Alertas y preferencias de la finca (`/farms/:farmId/alerts`). |
| `notifications.test.ts`, `components/NotificationBell.test.tsx` | Rutas del backend, comportamiento de la campana y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `notifications` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **avisar a tiempo**: tratamientos que vencen, stock bajo y el historial de avisos enviados. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Antes la campana y el banner estaban en `components/layout/` (como si fueran del layout) y la página en `pages/`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo usa `farms` (la finca activa, con `useFarm`). El layout de `app` monta la campana sin conocer su lógica. |
| **Contrato** — ¿Qué garantiza? | Leer el historial **no** envía avisos: los envía la tarea programada del backend. Las alertas próximas son, por defecto, las de los próximos 7 días. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `AppLayout` pone `<NotificationBell/>` en el encabezado; `app` monta `<AlertasPage>`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo los dos componentes de `index.ts`. Es una feature consumidora. |
