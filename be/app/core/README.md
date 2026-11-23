# `app/core` — Infraestructura transversal

| Archivo | Responsabilidad |
|---|---|
| `config.py` | Carga y valida las variables de entorno (Pydantic Settings). |
| `database.py` | Engine, `SessionLocal`, `Base` de los modelos y la dependencia `get_db()`. |
| `security.py` | Hash de contraseñas (bcrypt) y creación/validación de JWT. |
| `email.py` | Envío de correos con backend seleccionable (`smtp`, `resend`, `log`). |
| `limiter.py` | Instancia única del rate limiter. |
| `security_events.py` | Log JSON de eventos de seguridad (login, bloqueos, contraseñas, cierre de sesiones), con correo enmascarado. Lo usa identity por el puerto `SecurityLog`. |
| `error_handlers.py` | Traduce errores de dominio (`app.shared.exceptions`) a respuestas HTTP. |
| `audit_trail.py` | Tabla `audit_log` y `add_audit_log`: deja constancia de cada acción, dentro de la misma transacción. Es transversal, como el logging. La consulta de auditoría es del módulo `audit`. |

## Conceptos de arquitectura

| Concepto | Respuesta para `core` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De todo lo técnico que necesita cualquier módulo para funcionar: configuración, conexión a la BD, seguridad, correo, límites de peticiones y traducción de errores a HTTP. No contiene reglas de negocio. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: dar a los módulos la infraestructura lista para usar. Si un archivo empieza a hablar de fincas, bovinos o usuarios, no pertenece aquí. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Nada. `core` no importa ningún módulo, modelo, schema, servicio ni router; solo puede usar `app.shared`. Cambiar un módulo nunca obliga a cambiar `core`. |
| **Contrato** — ¿Qué garantiza? | `settings` validado al arrancar (la app no inicia si falta un secreto o es corto); `get_db()` siempre cierra la sesión; todo `DomainError` llega al cliente como `{"detail": "..."}` con el código correcto. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Solo la función que usa: `get_db`, `hash_password`, `create_access_token`, `send_generic_email`… No necesita saber si el correo sale por SMTP o Resend, ni cómo se firma el JWT. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia afuera: configuración, sesiones de BD, funciones de seguridad y correo. Hacia adentro: nada de dominio. La regla se verifica con **import-linter** (contrato *"core no depende del dominio"* en `pyproject.toml`). |
