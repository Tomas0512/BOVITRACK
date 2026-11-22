# Módulo `notifications` — Alertas y notificaciones (HU014)

**Endpoints:** `/api/v1/farms/{farm_id}/alerts`. Incluye alertas activas, `GET/PUT /preferences`, `GET /history` y `GET /history/unread-count` (solo leen). El envío lo hace la tarea programada `scheduler.py` y `PUT /history/{id}/read`.
**Tablas:** `user_notification_pref` y `notification_log`.
**Permiso:** módulo `fincas` (`can_read`).

| Concepto | Respuesta para `notifications` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De avisar a tiempo a quien tiene que actuar: detecta planes sanitarios vencidos o próximos e insumos en stock bajo, respeta las preferencias de cada usuario (canal, tipos activos) y deja un historial con estado de lectura. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: decidir **a quién**, **qué** y **por dónde** avisar. **No** decide qué cuenta como "plan vencido" ni como "stock bajo": eso lo responden salud e inventario por puertos. Antes el router repetía esas consultas; ahora banner y notificaciones usan la misma fuente. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Es el módulo con más vecinos (salud, inventario, identidad y correo), pero todos llegan como puertos de `app.shared.ports` y se conectan **solo** en `dependencies.py`. Si cambia la tabla de planes sanitarios, este módulo no se toca: recibe `SanitaryDue`, no el modelo ORM. |
| **Contrato** — ¿Qué garantiza? | **Idempotencia:** la misma alerta (tipo + referencia) no se repite al mismo usuario en 24 h. **Preferencias:** si no existen, se crean con `email`, todos los tipos activos y `real_time`. Un `False` desactiva el tipo. **Errores:** canal o frecuencia inválidos → `422` con el mensaje de siempre. Notificación ajena o inexistente → `404 "Notificación no encontrada o no pertenece al usuario"`. **El conteo de no leídas nunca envía correos.** |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | El router pide `active_alerts`, `run_notification_cycle`, etc. El servicio no sabe si el correo sale por SMTP, Resend o log: recibe un `EmailSender`. La hora también se inyecta (`now`) para poder probar la ventana de 24 h. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Entran DTOs inmutables (`SanitaryDue`, `LowStockItem`), IDs de miembros y correos. Salen diccionarios del banner, schemas del historial y correos. Ningún modelo ORM de otro dominio cruza hacia el servicio. |

## Cambio de comportamiento intencional

- En el ciclo de notificación, los insumos con stock bajo se procesan **del menor stock al mayor** (igual que en el banner). Antes el orden era el que devolviera la BD, sin garantía.

## Bugs corregidos

- **Consultar ya no envía correos.** Antes `GET /history` ejecutaba el motor y podía mandar emails solo por abrir la pantalla. Ahora el motor lo corre una **tarea programada** (`scheduler.py`): arranca con la app (con 30 s de espera inicial) y recorre todas las fincas activas cada `NOTIFICATIONS_INTERVAL_MINUTES` (15 por defecto; con 0 se desactiva). Si una finca falla, se registra el error y sigue con las demás. Como el motor es idempotente, varios procesos del backend no duplican avisos.
- **`total` en `/history` es el total real** de notificaciones con los filtros aplicados. Antes era el tamaño de la página (`len(items)`), y así no se podía paginar.

## Deuda conocida

- `reproductive` y `birth` existen como preferencias, pero el motor todavía no genera alertas de esos tipos.
- `frequency` (`daily`, `weekly`) se guarda pero no se usa: todo se envía en tiempo real.
