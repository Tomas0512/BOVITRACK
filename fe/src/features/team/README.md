# Feature `team` — El equipo de una finca

Consume el módulo `team` del backend: `/api/v1/farms/{farm_id}/roles` y `/employees…`, las rutas públicas `/api/v1/auth/invitation/{token}`, `/register-invited` y `/request-reactivation`, y la moderación `/api/v1/admin/reactivation-requests`.

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: `EmployeeList`, `InvitedRegisterPage`, `RequestReactivationPage` y `ReactivationRequestsPage`. |
| `api.ts` | Roles, empleados, cuenta de un empleado, invitaciones y reactivación. |
| `components/` | `EmployeeList` (pestaña de empleados de la finca) y `AssignEmployeeModal` (invitar). |
| `pages/` | Registro por invitación y solicitud de reactivación (públicas), y moderación de reactivaciones (`/admin/reactivations`, solo Administrador). |
| `team.test.ts` | Rutas del backend y API pública. |
| `pages/ReactivationRequestsPage.test.tsx` | Listar, aprobar y rechazar con confirmación, errores del backend y estado vacío. |

## Conceptos de arquitectura

| Concepto | Respuesta para `team` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De las personas que trabajan en una finca: invitarlas, cambiar su rol o estado, cerrar su cuenta y recuperar el acceso. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Reúne lo que estaba repartido entre `api/employees.ts`, `api/auth.ts` (invitación y reactivación), `components/employees/` y dos páginas sueltas. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Usa `identity` solo por su API pública: `useAuth` (para saber quién es el usuario actual) y el tipo `UserResponse`. Si identity reorganiza su sesión, team no cambia. |
| **Contrato** — ¿Qué garantiza? | Las mismas rutas del backend. Los errores (último administrador, invitación vencida…) llegan con el mensaje real del backend. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | La página de la finca usa `<EmployeeList farmId>`; `app` monta las páginas en sus rutas (la de moderación, dentro de `RequireRole role="Administrador"`). |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo los cuatro componentes de `index.ts`. |

**Código muerto eliminado:** `assignEmployee` y `EmployeeAssign`. Llamaban a `POST /farms/{id}/employees`, que el backend no tiene, y nadie los usaba.

## Moderación de reactivaciones

Pantalla `/admin/reactivations` (menú **Reactivaciones**, visible solo para Administrador). Lista las solicitudes pendientes y permite aprobarlas (la cuenta vuelve a iniciar sesión) o rechazarlas, siempre con confirmación. El **alcance lo decide el backend**: solo aparecen personas que fueron miembros de alguna finca que el usuario administra. Si el backend responde 403, la pantalla muestra su mensaje.
