# Módulo `identity` — Usuarios, autenticación, roles y permisos (capa base)

**Endpoints:**
- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/forgot-password`, `/reset-password`, `/verify-email`, `/logout-all`
- `GET /api/v1/users/me` (perfil con el rol más reciente) y `DELETE /api/v1/users/me` (baja de la cuenta propia)

Las rutas `/api/v1/auth/invitation/{token}`, `/register-invited` y `/request-reactivation` son del módulo `team` (`team/router/public.py`). Tienen el mismo prefijo y el mismo tag, así que el cliente no nota la diferencia.

**Tablas propias:** `users`, `password_reset_tokens`, `email_verification_tokens`, `role`, `permission` y `user_farm` (membresía usuario-finca-rol).

| Archivo | Responsabilidad |
|---|---|
| `__init__.py` | API pública: guards, puertos, `User`, `UserResponse`/`MessageResponse` y `DocumentType` (que vive en `shared`). |
| `router.py` | `auth_router` (`/api/v1/auth`) y `users_router` (`/api/v1/users`), unidos en `router`. |
| `dependencies.py` | Arma los servicios. Define `get_current_user` y `require_permission`, los guards de **toda** la API, y los puertos para otros módulos. |
| `service/auth.py` | Registro, login con bloqueo (`LoginThrottle`), tokens, recuperación de contraseña y verificación de correo. |
| `service/account.py` | Perfil y baja de la cuenta propia. |
| `service/access.py` | La regla RBAC: membresía activa → rol activo → permiso del módulo. |
| `repository.py` | `UserRepository` (usuarios y tokens) y `MembershipRepository` (membresías, roles y permisos). |
| `schemas.py` | Entradas (registro, login, contraseña) y salidas (`UserResponse`, `TokenResponse`, `MessageResponse`). |
| `models/` | `User`, los dos tokens, `Role`/`Permission` y `UserFarm` (`membership.py`). |

## Conceptos de arquitectura

| Concepto | Respuesta para `identity` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **quién** es el usuario (autenticación) y de **qué puede hacer** en cada finca (roles, permisos y membresías). |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: identidad y acceso. Por eso `UserFarm` salió de `models/farm.py`: la membresía es la pieza con la que se decide un permiso. Invitar empleados o moderar reactivaciones usa identity, pero es gestión del equipo de una finca: va al módulo `team`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | identity es la **capa base**: no importa ningún módulo, solo `core` y `shared`. La membresía guarda `farm_id` (la llave foránea), pero no navega hacia la finca. El rastro de auditoría (`core`) ya no tiene relación ORM hacia `User`. Que identity no cargue ningún otro módulo lo prueba `test_identity_is_the_base_layer_and_boots_like_uvicorn`. |
| **Contrato** — ¿Qué garantiza? | Token inválido, expirado, de una sesión cerrada o de un usuario inexistente → `401` con `WWW-Authenticate: Bearer`. Cuenta desactivada → `403`. 5 claves erradas seguidas bloquean ese correo 15 minutos (`429`). Sin membresía activa, rol activo o permiso → `403`, con un mensaje distinto para cada caso. Los mensajes son los mismos de antes del refactor. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Un router solo escribe `Depends(require_permission("bovinos", "can_create"))` y recibe un `CurrentUser` (un puerto de `shared` con solo `id`): no conoce JWT, bcrypt ni la tabla `user_farm`. Otros módulos piden datos por puertos: `build_farm_member_lookup` y `build_user_email_lookup` (notifications), `has_permission_anywhere` (audit), y `build_membership_check`, `build_admin_granter` y `build_member_farm_ids` (farms: así farms no escribe en `user_farm`). |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia afuera: los guards, los puertos, `User` y `UserResponse`/`MessageResponse`/`DocumentType`. Cada módulo recibe los guards **por su propio `dependencies.py`**, que los re-exporta, nunca directo desde el router. Nunca salen la contraseña hasheada ni los tokens de un solo uso. Lo verifica import-linter: identity es el último nivel de *"capas de módulos"*. |

## Cambios de comportamiento en 3e-2

- **Bug corregido:** al registrarse se creaban **dos** tokens de verificación y solo se enviaba uno. Ahora se crea uno solo, el que se envía.
- **Registro atómico:** el usuario y su registro de auditoría se confirman en una sola transacción.
- **Todo `401` incluye `WWW-Authenticate: Bearer`**, como pide el estándar HTTP. Antes, dos casos del refresh lo omitían.
- **Un token con un `sub` que no es UUID** ahora da `401`. Antes daba `500`.
- **Bug corregido (#16):** un empleado **desactivado** en la finca ya no puede recibir tareas nuevas. Antes se aceptaban, aunque él no podía abrirlas (`require_permission` le daba `403`). El dueño de la finca sigue pudiendo recibirlas. Las tareas que ya tenía asignadas no se tocan.

## Deuda conocida

- `LoginThrottle` vive en memoria: se pierde al reiniciar y no se comparte entre réplicas. **Decidido:** se pasa a la BD (o Redis) en la Parte 5/6, junto con el despliegue.
