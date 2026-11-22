# Módulo `inventory` — Inventario de alimentos e insumos (HU011)

**Endpoints:** `/api/v1/farms/{farm_id}/food`. Incluye el CRUD de insumos, `POST/GET /consumptions`, `POST /purchases`, `POST /adjust-stock`, `GET /movements` y `GET /low-stock`. Además, `POST /api/v1/farms/{farm_id}/calves/{bovine_id}/feeding-plan` (plan de alimentación de terneros, con etiqueta "Terneros (HU007)").
**Tablas:** `food`, `consumption` y `stock_movement`.
**Permiso:** módulo `alimentos`.
**Lo usan otros módulos:** `notifications` (stock bajo) y `health` (¿este alimento es de la finca?).

| Concepto | Respuesta para `inventory` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De saber cuánto hay de cada insumo y por qué cambió: consumos (restan), compras (suman y fijan el costo) y ajustes manuales. Cada cambio queda registrado con el stock de antes y el de después. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: el stock y su trazabilidad. La definición de "stock bajo" vive **aquí**, porque el inventario es el dueño del dato; antes estaba repetida en el router de alertas y en el motor de notificaciones. Validar bovinos, lotes y potreros no es de este módulo: llega por puertos. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Depende solo de **livestock** (¿el bovino del consumo o del plan es de la finca?), por su API pública. En las capas de módulos está entre salud (arriba) y ganado (abajo). Alcance de finca y potreros llegan por puertos de farms; la auditoría, por `core`. Otros módulos dependen de él, pero solo a través de `build_low_stock_lookup` y `build_food_lookup`. |
| **Contrato** — ¿Qué garantiza? | **El stock nunca queda negativo**: un consumo mayor al disponible responde `400 "Stock insuficiente. Disponible: …"`, y un ajuste que lo dejaría bajo 0 responde `400`. Todo cambio de stock genera un `StockMovement`. Un consumo solo apunta a un bovino, lote o potrero de la finca, y el potrero tiene que ser del lote indicado; si no se indica lote, se toma el del potrero. Insumo inexistente o de otra finca → `404 "Alimento no encontrado"`. Eliminar un insumo es un borrado lógico. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Notificaciones recibe una función `farm_id -> [LowStockItem]`. No sabe que existe la tabla `food` ni cómo se compara contra el mínimo. Salud recibe `(farm_id, food_id) -> bool`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia otros módulos solo salen DTOs inmutables (`LowStockItem`) o booleanos, nunca el modelo `Food`. De otros dominios entra `PaddockRef(id, land_plot_id)`. |

## Plan de alimentación de terneros (llegó en la Parte 3d)

`CalfFeedingService` valida que el ternero sea de la finca (puerto hacia ganado), que el alimento sea de la finca y que la cantidad sea positiva. Antes vivía en ganado y consultaba la tabla `food`, lo que creaba un ciclo de dependencias inventario ↔ ganado.

## Bugs corregidos (después de la Parte 3d)

- **El plan de alimentación ya no responde 500.** El cuerpo se valida con `CalfFeedingPlanCreate`, un schema que existía pero no se usaba. Ahora vive en este módulo, junto con el plan. Las fechas llegan como fechas, y un cuerpo inválido (fecha mal escrita, fin antes que inicio, sin `food_id`) responde `422` con el detalle de Pydantic. Antes el endpoint recibía un `dict` sin validar y fallaba al llamar `.isoformat()` sobre un texto.

## Deuda conocida

- **El plan de alimentación no se guarda**: solo se valida y se devuelve. Persistirlo requiere una tabla nueva y una migración.

- **Se puede operar sobre un insumo eliminado.** `get_food` no filtra por `is_active`, así que se puede consumir, comprar o ajustar un insumo dado de baja, y `GET /food/{id}` lo devuelve.
- El mensaje del ajuste negativo está en inglés (`"Cannot reduce stock below 0…"`).
