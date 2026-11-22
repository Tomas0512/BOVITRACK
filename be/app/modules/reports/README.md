# Módulo `reports` — Reportes y estadísticas

**Endpoints:**
- `GET /api/v1/farms/{farm_id}/statistics`: permiso `fincas`.
- `GET /api/v1/farms/{farm_id}/milk-daily`: permiso `produccion_leche`.
- `GET /api/v1/reports/farm-summary`, `/low-stock-alerts` y `/pending-tasks`: solo exigen sesión y se acotan a las fincas del usuario.
- `GET /api/v1/farms/{farm_id}/reports?category=&start_date=&end_date=&export=json|excel|pdf`: permiso `fincas` y límite de 10 por minuto.

**Tablas propias:** ninguna. Es un **modelo de lectura** sobre vistas SQL (`v_farm_summary`, `v_low_stock_alerts`, `v_pending_tasks`, `v_milk_production_daily`), la función `fn_farm_statistics` y agregados.

| Archivo | Capa | Responsabilidad |
|---|---|---|
| `router.py` | HTTP | Parsear los parámetros y armar la descarga (tipo de contenido y nombre del archivo). |
| `dependencies.py` | Composición | Arma `ReportService` con su repositorio. |
| `service.py` | Negocio | Validar el rango de fechas, decidir qué categorías incluir, calcular promedios y totales. |
| `exporters.py` | Formato | Pasar `ReportResponse` a Excel o PDF, sin consultas ni cálculos. |
| `schemas.py` | Contrato | `ReportFilterParams`, `ReportResponse` y los sub-reportes. |
| `repository.py` | Datos | Todo el SQL de lectura, más la lista blanca de vistas. |

## Conceptos de arquitectura

| Concepto | Respuesta para `reports` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De dar una foto consolidada de la operación: estadísticas de la finca, producción diaria, resúmenes de todas las fincas del usuario y un reporte productivo, sanitario o económico, descargable. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: **leer y presentar**. Nunca escribe. Cada capa cambia por un motivo distinto: una consulta nueva va al repositorio, una regla de cálculo al servicio y un formato nuevo (CSV, por ejemplo) a `exporters.py`. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | **Cero acoplamiento en Python** con otros módulos: no importa sus modelos ni sus servicios. Sí está acoplado **al esquema de la BD** (tablas y vistas de leche, bovinos, tratamientos, planes y economía). Es una excepción consciente: un reporte necesita leer de todos. Si cambia una columna, solo se revisa `repository.py`. |
| **Contrato** — ¿Qué garantiza? | Los resúmenes globales solo incluyen fincas donde el usuario es dueño o miembro activo. **Errores:** rango invertido, fechas futuras o mal escritas → `422`. Finca inexistente → `404 "Farm not found"`. Vista fuera de la lista blanca → `400`, **antes** de consultar la BD. **Salida:** JSON (`ReportResponse`), `.xlsx` o `.pdf`. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | El router pide `generate_report(farm_id, params)` y recibe un `ReportResponse`. No sabe que detrás hay vistas, funciones de Postgres ni `CASE` de SQL. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Entran IDs, filtros y el usuario. Salen diccionarios y schemas de solo lectura, o bytes de un archivo. El nombre de una vista **nunca** cruza desde el usuario hacia el SQL sin pasar por `ALLOWED_REPORT_VIEWS`. |

## Bugs corregidos

- **`pending_treatments` ya se calcula:** cuenta los tratamientos con una próxima aplicación (`next_application_date`) de hoy en adelante, es decir, las dosis que faltan por aplicar. Antes siempre era 0. No depende del rango de fechas del reporte, porque mira hacia adelante.
- **Fecha con formato inválido → 422** con el mensaje `"Fecha inválida en start_date: use el formato YYYY-MM-DD"`. Antes respondía 500.

## Deuda conocida

- El reporte económico suma también registros de tipo `gasto`, pero el módulo `economics` solo acepta `ingreso` y `egreso`. Es un resto de una versión anterior.
- `GET /reports/farm-summary` y sus hermanos no exigen ningún permiso de módulo; basta con tener sesión. Se compensa porque se acotan a las fincas del usuario.
