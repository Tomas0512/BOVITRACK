# Módulo `economics` — Información económica

**Endpoints:** `/api/v1/farms/{farm_id}/economics` (CRUD, más `GET /indicators`)
**Tabla:** `economic_record`
**Permiso:** módulo `economica`

| Concepto | Respuesta para `economics` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De registrar los ingresos y egresos de la finca y de calcular sus indicadores: balance total y del mes, totales por categoría y promedio diario. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: saber si la finca gana o pierde dinero. El cálculo de indicadores vive en el servicio, porque es regla de negocio; el repositorio solo entrega los registros. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Es el módulo más independiente: solo depende de la auditoría, inyectada como `AuditRecorder`. Nadie depende de él. |
| **Contrato** — ¿Qué garantiza? | **Entrada:** `EconomicRecordCreate` valida que el tipo sea `ingreso` o `egreso` y que la categoría corresponda a ese tipo. **Salida:** `EconomicRecordResponse` y `EconomicIndicators` (montos en `Decimal`). **Errores:** registro inexistente o de otra finca → `404 "Registro economico no encontrado"`. El listado sale ordenado del más reciente al más antiguo. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Solo `api_router` y los schemas de respuesta. La fecha de "hoy" también se inyecta (`today`), así el cálculo mensual se puede probar con una fecha fija. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Entran JSON validado e IDs; salen schemas o `NotFoundError`. Ni la sesión de BD ni `HTTPException` cruzan hacia el servicio. |

## Bugs corregidos

- **Promedio diario con rango:** ahora divide por los N días del rango, contando ambos extremos (del 1 al 10 son 10 días). Antes dividía por N−1.
