# Módulo `livestock` — Ganado (bovinos, pesajes, terneros y movimientos)

**Endpoints:**

| Ruta | Qué hace | Permiso |
|---|---|---|
| `/api/v1/farms/{farm_id}/bovines` | CRUD de la ficha, `GET /breeds`, `POST /import` (CSV) | `bovinos` |
| `/api/v1/farms/{farm_id}/bovines/{bovine_id}/weights` | Pesajes: registrar, listar, detalle, eliminar | `bovinos` |
| `/api/v1/farms/{farm_id}/calves` | Terneros (HU007): listado, resumen, ficha con métricas, curva de peso, pesaje | `bovinos` |
| `/api/v1/farms/{farm_id}/movements` | Movimientos (HU009): registrar, listar, detalle. Son **inmutables** | `bovinos` |

**Tablas:** `bovine`, `bovine_identification`, `bovine_audit`, `weight` y `animal_movement`.
**Lo usan otros módulos:** `build_bovine_lookup` (inventory, health, reproduction, milk_production, documents, tasks) y `build_calf_registrar` (reproduction).

| Carpeta | Contenido |
|---|---|
| `router/` | Un router por agregado (`bovines`, `weights`, `calves`, `movements`), unidos en `router`. |
| `service/` | `BovineService` (incluye la importación CSV y el registro de crías), `WeightService`, `CalfService` y `MovementService`. |
| `repository.py` | `BovineRepository`, `WeightRepository` y `MovementRepository`. |
| `models/`, `schemas/` | Un archivo por agregado. |

## Conceptos de arquitectura

| Concepto | Respuesta para `livestock` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Del animal: su ficha (identificación, genealogía, ubicación, estado), su peso en el tiempo, el seguimiento especial de los terneros y sus entradas y salidas del hato. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: todo gira alrededor del bovino. Las reglas puras de terneros (peso esperado por raza y edad, plan por edad) son funciones sin estado en `service/calves.py`. El **plan de alimentación** se mudó a `inventory`: lo que valida es un alimento, y dejarlo aquí creaba un ciclo de dependencias. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Solo depende de módulos de niveles más bajos: farms (lotes, potreros, alcance de finca, búsqueda por nombre en el CSV) e identity (guards). Seis módulos dependen de él, siempre por su API pública. En las capas de módulos está encima de farms e identity. |
| **Contrato** — ¿Qué garantiza? | **Bovinos:** identificación única en la finca (`409`). Padre, madre, lote y potrero deben ser de la finca, y el potrero coherente con el lote (`400`); si no se indica lote, se toma el del potrero. Bovino y auditoría se guardan en la misma transacción. Retirar es un borrado lógico. **Pesajes:** solo de bovinos activos (`404`). Ganancia diaria = (nuevo − anterior) / días. El peso actual solo cambia si el pesaje es el más reciente. **Terneros:** como máximo 365 días (si no, `400`); no se aceptan pesajes antes del nacimiento ni dos el mismo día (`400`). **Movimientos:** venta → vendido, muerte → muerto (sale del hato con fecha y motivo); compra, traslado o nacimiento → activo. No se repite el mismo tipo el mismo día (`400`). **No se editan ni se eliminan** (`403`). |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Los otros módulos reciben `BovineRef(id, sex)` o un `uuid`. No conocen la tabla `bovine` ni el modelo ORM. La fecha de "hoy" se inyecta en terneros para probar edades con una fecha fija. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia afuera salen `BovineRef` y el id de la cría registrada. Hacia adentro entran `PaddockRef`, ids de lote resueltos por nombre (CSV) y booleanos. La importación CSV recibe **texto**; leer el archivo subido es tarea del router. |

## Cambios de este refactor

- **El plan de alimentación de terneros se mudó a `inventory`.** Conserva la misma URL, etiqueta, `operationId` y permiso. Rompe el ciclo inventario ↔ ganado que detectó import-linter.
- **`ensure_farm_scope` ya no importa el modelo `Bovine`.** Recibe el buscador de bovinos (`find_bovine`). Antes, todo módulo que validaba alcance dependía en secreto de ganado.
- **La inmutabilidad de los movimientos es una regla del servicio** (`PermissionDeniedError` → 403, con el mismo mensaje). Antes estaba escrita en el router. Se eliminó el código de "conciliación de estado" de editar y eliminar, que nunca se ejecutaba porque esos endpoints siempre respondían 403.
- **La importación CSV se interpreta en el servicio.** Los lotes y potreros por nombre se resuelven con un puerto. Antes el router hacía consultas a la base de datos.

## Bugs corregidos (después de la Parte 3d)

- **La curva de peso de terneros ya no responde 500.** Leía `weight.daily_gain_kg`, pero el modelo tiene `daily_gain`.
- **CSV: cada error se informa con su número de línea real.** Antes, los errores de registro (por ejemplo, una identificación repetida) se numeraban contando solo las filas válidas. Además, `total` cuenta ahora todas las filas de datos y `failed` todas las que no se importaron, incluidas las de formato inválido.
- **Borrar el pesaje más reciente recalcula el peso actual**, que vuelve al pesaje anterior. Borrar un pesaje más viejo no lo cambia. Si no queda ningún pesaje, se conserva el último valor conocido.

## Deuda conocida

- Las verificaciones de duplicados usan `scalar_one_or_none()`. Si ya hubiera duplicados en la base (datos viejos), responderían 500 en vez de 409 o 400.
