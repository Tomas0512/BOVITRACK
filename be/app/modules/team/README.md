# Módulo `team` — El equipo de una finca

**Endpoints:**
- `/api/v1/farms/{farm_id}`: `GET /roles`, `POST /employees/invite`, `GET /employees`, `PUT /employees/{user_id}`, `PUT /employees/{user_id}/account` y `DELETE /employees/{user_id}`.
- `/api/v1/admin/reactivation-requests`: listar, aprobar (`/{id}/approve`) y rechazar (`/{id}/reject`).
- Públicas, bajo `/api/v1/auth` y con el tag "Autenticación", igual que antes: `GET /invitation/{token}`, `POST /register-invited` y `POST /request-reactivation`.

**Tablas propias:** `farm_invitation` y `reactivation_request`.
**Permisos:** los endpoints de empleados exigen `usuarios:*`. Cerrar o abrir una cuenta exige, además, ser **Administrador de esa finca**. Moderar reactivaciones exige ser Administrador de alguna finca.

| Archivo | Responsabilidad |
|---|---|
| `__init__.py` | API pública: solo `api_router` (nadie depende de team). |
| `router/` | `employees.py`, `admin.py` (moderación) y `public.py` (rutas sin sesión), unidos en `router`. |
| `dependencies.py` | Arma los servicios y el guard `require_admin_role`. Es el único archivo que conoce a identity y farms. |
| `service/employees.py` | Reglas del equipo, entre ellas que la finca nunca se queda sin Administrador. |
| `service/invitations.py` | Invitar, ver la invitación y registrarse o vincularse por invitación. |
| `service/reactivation.py` | Pedir la reactivación y el alcance del moderador. |
| `repository.py` | Invitaciones, solicitudes y `Transaction` (confirma la unidad de trabajo). |
| `schemas/`, `models/` | Empleados, invitaciones y reactivación. |

## Conceptos de arquitectura

| Concepto | Respuesta para `team` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **las personas que trabajan en una finca**: quién entra (invitación), con qué rol, quién sale, y cómo recupera el acceso alguien cuya cuenta se cerró. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: gestionar el equipo. No es identity: identity sabe *quién eres y qué puedes hacer*; team decide *cómo cambia el equipo*. Por eso las reglas de team (último administrador, quién puede ofrecer el rol Administrador, el alcance del moderador) están aquí, y los datos de usuarios, roles y membresías se quedan en identity. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | team no escribe SQL sobre tablas de otros módulos. Pide usuarios, roles y membresías al puerto de identity (`build_membership_directory`), el hash de contraseñas a `build_password_hasher`, y el nombre de la finca a farms (`build_farm_name_lookup`). Si identity cambia sus tablas, team no cambia. Lo prueba `test_team_only_loads_identity_and_farms_and_boots_like_uvicorn`. |
| **Contrato** — ¿Qué garantiza? | Una finca **nunca** se queda sin Administrador activo: no se le puede desactivar, desvincular, cerrar la cuenta ni quitar el rol al último (`400`). Solo un Administrador ofrece el rol Administrador (`403`). Una invitación es de un solo uso y vence en 72 h; al crear una nueva, las anteriores quedan anuladas. Un moderador solo ve solicitudes de personas de **sus** fincas; las demás le responden `404`. Los mensajes son los mismos de antes. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Los routers llaman `service.invite(...)`, `service.update(...)`, `service.approve(...)`. Los servicios ven a identity como un `Protocol` (`TeamDirectory`, `InvitationDirectory`, `ReviewerDirectory`) con solo los métodos que usan. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia afuera: solo `api_router`. Hacia adentro: las APIs públicas de identity y farms, y solo por `dependencies.py`. Nunca salen la contraseña ni el token de una invitación (el token solo viaja por correo). Lo verifica import-linter: team está en el nivel de los consumidores en *"capas de módulos"*. |

## Bugs corregidos en 3e-4

| # | Antes | Ahora |
|---|---|---|
| 20 | Se le podía **cambiar el rol** al único Administrador de una finca, y la finca quedaba sin administrador. Desactivarlo o desvincularlo sí estaba protegido. | `400 "No se puede quitar el rol Administrador al último administrador activo de la finca…"`. |
| 21 | Al invitar, la auditoría guardaba `entity_id = "None"`: se escribía antes de que la invitación tuviera id. | Guarda el id real de la invitación. |

**Código muerto eliminado:** `assign_employee` y el schema `EmployeeAssign`. Ningún endpoint los usaba, así que el OpenAPI no cambia. También se quitó la validación de contraseña repetida en el servicio de invitaciones: el schema `InvitedRegister` ya la hace antes (422).

## Cambios de la Parte 6b (seguridad)

- `POST /api/v1/auth/request-reactivation` responde **siempre** `202` con el mismo mensaje, exista o no el correo y esté activa o no la cuenta. Ya no devuelve el `user_id`. Antes daba `404 "Correo no registrado"` o `400 "La cuenta ya está activa"`, y con eso cualquiera podía averiguar qué correos estaban registrados. La solicitud se sigue creando solo si la cuenta existe, está desactivada y no tiene otra pendiente. Esto lo decidió el usuario y funciona igual que `/forgot-password`.

## Deuda conocida

Ninguna pendiente. La reparación de `seed_roles.py` que chocaba con `uq_user_farm` se corrigió en la Parte 6b-2: ahora reactiva el vínculo existente del dueño.
