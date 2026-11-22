# `app/shared` — Piezas comunes de Python puro

| Archivo | Responsabilidad |
|---|---|
| `exceptions.py` | Errores de dominio: `DomainError`, `NotFoundError` (404), `ConflictError` (409), `BusinessRuleError` (400), `PermissionDeniedError` (403), `InvalidRequestError` (422), `AuthenticationError` (401, con `WWW-Authenticate: Bearer`) y `TooManyAttemptsError` (429). |
| `ports.py` | Interfaces (`Protocol`) con las que un módulo le pide algo a otro sin conocerlo: `CurrentUser`, `AuditRecorder`, `BovineLookup`, `FarmMemberLookup`, `FarmMembershipCheck`, `UserEmailLookup`… La implementación la entrega el módulo dueño por su API pública. |

## Conceptos de arquitectura

| Concepto | Respuesta para `shared` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De definir piezas que todos los módulos usan igual y que no dependen de ninguna tecnología, como el vocabulario común de errores. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: un lenguaje común entre módulos. Lo que necesite BD, HTTP o un dominio concreto no va aquí. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Nada. `shared` no importa nada de la app y tampoco FastAPI ni SQLAlchemy. Es la capa más estable: todos dependen de ella y ella de nadie. |
| **Contrato** — ¿Qué garantiza? | Cada error trae un `message` legible para el usuario. El significado de cada clase es fijo: `NotFoundError` = no existe, `ConflictError` = ya existe o choca con el estado actual, etc. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Qué pasó, no cómo se responde. Un servicio lanza `NotFoundError("Bovino no encontrado")` sin saber que eso se convierte en un 404. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Solo tipos y valores de Python puro. Se verifica con **import-linter** (contrato *"shared es Python puro"*, que prohíbe `fastapi`, `sqlalchemy` y cualquier paquete de la app). |
