# Feature `identity` — Sesión y acceso

Consume el módulo `identity` del backend (`/api/v1/auth/*` y `/api/v1/users/me`).

| Carpeta / archivo | Responsabilidad |
|---|---|
| `index.ts` | API pública: sesión, guards, pantallas de acceso y `deleteAccount`. |
| `api.ts` | Registro, login, recuperación de contraseña, verificación de correo, perfil y baja de la cuenta. |
| `types.ts` | Tipos de la sesión (`UserResponse`, `AuthContextType`…). |
| `session/` | `AuthProvider` (estado de la sesión), `useAuth`, aviso de inactividad (`useSessionTimeout`, `SessionGuard`). |
| `components/` | Guards de rutas: `ProtectedRoute` (exige sesión) y `RequireRole` (exige un rol). |
| `pages/` | Login, registro, olvidé mi contraseña, restablecer contraseña y verificar correo. |
| `identity.test.tsx` | Guards, rutas del backend y API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `identity` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **quién** usa la app: abrir, mantener y cerrar la sesión, y proteger las rutas privadas. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí. Invitaciones y reactivación de cuentas estaban en `api/auth.ts`, pero son del equipo de una finca y pasaron a `features/team`, igual que en el backend. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo usa `@/core/http` y `@/shared/layout`. La renovación del token no está aquí: la hace el interceptor de `core/http`. Por eso se eliminó `refreshToken()`, que nadie usaba. |
| **Contrato** — ¿Qué garantiza? | Sin sesión, una ruta privada lleva a `/login`. Mientras la sesión carga, no decide. `RequireRole` deja pasar solo al rol indicado. `useAuth` fuera del proveedor lanza un error claro. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | `app` envuelve con `<AuthProvider>` y protege con `<ProtectedRoute>`. Las features usan `useAuth()` y no saben dónde se guardan los tokens. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo lo que exporta `index.ts`, más el tipo `UserResponse`. `api.ts`, `session/` y los demás tipos son internos (ESLint rechaza `@/features/identity/...`). |
