# Módulo `milk_production` — Producción lechera

**Endpoints:** `/api/v1/farms/{farm_id}/milk-production` (CRUD, más `GET /summary`)
**Tabla:** `milk_production`
**Permiso:** módulo `produccion_leche`

| Concepto | Respuesta para `milk_production` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De registrar cada ordeño (litros, fecha, sesión y tipo) por bovino o por lote, y de resumir la producción de un periodo: total, promedio diario, días con ordeño, totales por sesión y por tipo, y el top 10 de bovinos. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: medir cuánta leche produce la finca. Saber si un bovino o un lote es de la finca **no** es de este módulo, por eso lo pregunta a colaboradores (`BovineLookup`, `LandPlotLookup`). |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Depende de tres puertos (bovinos, lotes y auditoría), conectados **solo** en `dependencies.py`. Si cambia la tabla de bovinos, este módulo no se entera: recibe un `BovineRef`, no el modelo ORM. |
| **Contrato** — ¿Qué garantiza? | **Reglas:** todo ordeño va asociado a un bovino o a un lote, y ese bovino o lote debe ser de la finca. No puede haber dos ordeños del mismo bovino en la misma fecha y sesión. **Errores (400):** "Debe indicar un bovino o un lote para el ordeño", "El bovino indicado no existe en esta finca", "El lote indicado no existe en esta finca", "Ya existe un ordeño registrado para este bovino en esa fecha/sesión". **404:** "Registro de producción no encontrado". **Salida:** `MilkProductionResponse`. El resumen devuelve los montos como texto para no perder precisión. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Solo `api_router` y `MilkProductionResponse`. El servicio no sabe cómo se busca un bovino; solo recibe `BovineRef(id, sex)` o `None`. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Entran JSON validado e IDs. Salen schemas, un diccionario de resumen o errores de dominio. De ganado solo cruza `BovineRef`, nunca el modelo `Bovine`. |

## Deuda conocida

- `GET /summary` no declara `response_model`: devuelve un diccionario libre, así que su forma no aparece documentada en Swagger.

## Bugs corregidos

- **Duplicados previos ya no dan 500.** Si la BD ya tenía dos ordeños iguales (datos viejos), crear o editar otro respondía 500. Ahora responde 400 con el mensaje de duplicado.
