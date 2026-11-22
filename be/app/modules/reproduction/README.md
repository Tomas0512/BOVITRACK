# Módulo `reproduction` — Control reproductivo

**Endpoints:** `/api/v1/farms/{farm_id}/reproductive-events` (CRUD)
**Tabla:** `reproductive_event`
**Permiso:** módulo `reproductivo`

| Concepto | Respuesta para `reproduction` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De registrar el ciclo reproductivo de cada hembra (celo, servicio, diagnóstico, parto…), de calcular la fecha probable de parto y de pedir que se registren las crías cuando hay un parto. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: seguir la reproducción del hato. Las reglas reproductivas viven aquí: gestación de 283 días, solo las hembras paren, la identificación provisional de la cría (`CRIA-…`). **Crear el bovino** no: eso es de ganado y se pide por un puerto. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Usa cuatro puertos: `BovineLookup`, `CalfRegistrar`, `FarmScopeChecker` y `AuditRecorder`. Todos se conectan **solo** en `dependencies.py`. Si ganado cambia cómo registra un bovino, este módulo no se toca. |
| **Contrato** — ¿Qué garantiza? | **Reglas:** madre, toro y cría deben ser de la finca. Un parto solo lo registra una hembra. Un `servicio` sin `due_date` recibe `event_date + 283 días`. Un `parto` con resultado `macho`, `hembra` o `gemelos` crea 1 o 2 crías y enlaza la primera en `calf_id`. **Errores (400):** "El bovino indicado no existe en esta finca", "Solo una hembra puede registrar un parto", "El toro indicado no existe en esta finca", "La cría indicada no existe en esta finca". **404:** "Evento reproductivo no encontrado". **Atomicidad:** el evento y sus crías se guardan en la misma transacción. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Solo `api_router` y `ReproductiveEventResponse`. El servicio no sabe cómo se guarda un bovino: llama a `register_calf(...)` y recibe un id. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia ganado salen solo datos simples (identificación, sexo, fecha, madre) y vuelve un `uuid`. De ganado entra `BovineRef(id, sex)`, nunca el modelo `Bovine`. |

## Deuda conocida

- `tests/test_reproductive_event.py` (anterior al refactor) prueba una **copia** de la función de crías, no el código real. Las pruebas reales del módulo están en `tests/test_modules_3a.py`.
- Al crear, la validación de madre, toro y cría usa mensajes propios (sin punto final). Al actualizar se usa el validador común (`ensure_farm_scope`), cuyos mensajes terminan en punto. Se mantiene así para no cambiar comportamiento.
