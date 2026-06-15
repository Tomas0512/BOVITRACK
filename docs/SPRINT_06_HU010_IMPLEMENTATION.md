# HU010 — Información Económica: Documentación de Implementación

## Resumen

Módulo completo de registro y consulta de información económica para fincas
ganaderas. Permite registrar ingresos y egresos categorizados, consultar
indicadores financieros con filtros por fecha, y visualizar dashboards.

**Responsable:** Edwin Delgado
**Branch:** `feature/sprint6-edwin`
**Estado:** ✅ Completada

---

## Estructura del Módulo

```
be/
├── app/
│   ├── models/
│   │   └── economics.py              # Modelo ORM EconomicRecord
│   ├── schemas/
│   │   └── economics.py              # Pydantic schemas + EconomicIndicators
│   ├── services/
│   │   └── economics_service.py      # Lógica CRUD + cálculo de indicadores
│   └── routers/
│       └── economics.py              # Endpoints REST (CRUD + /indicators)
├── alembic/versions/
│   └── k1l2m3n4o5p6_create_economic_record_table.py  # Migración
fe/
├── src/
│   ├── api/
│   │   └── economics.ts              # Cliente API TypeScript
│   └── pages/
│       └── EconomicDashboard.tsx     # Dashboard con Recharts
```

---

## Scripts de Base de Datos

### Migración: `k1l2m3n4o5p6_create_economic_record_table.py`

**Qué hace:** Crea la tabla `economic_record` con los siguientes campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID (PK) | Identificador único |
| `farm_id` | UUID (FK → farm) | Finca a la que pertenece |
| `registered_by` | UUID (FK → user) | Usuario que registró |
| `record_type` | ENUM('ingreso','egreso') | Tipo de movimiento |
| `category` | VARCHAR(50) | Categoría (ver catálogo) |
| `amount` | NUMERIC(12,2) | Valor del movimiento |
| `record_date` | DATE | Fecha del movimiento |
| `description` | TEXT (nullable) | Descripción opcional |
| `reference_type` | VARCHAR(50) (nullable) | Tipo de entidad referenciada |
| `reference_id` | UUID (nullable) | ID de entidad referenciada |
| `is_active` | BOOLEAN | Soft delete |
| `created_at` | TIMESTAMP | Auditoría |
| `updated_at` | TIMESTAMP | Auditoría |

**Índices:** farm_id, record_type, category, record_date

**Ejecución:**
```bash
cd be
alembic upgrade head
```

### Seed de Permisos

Archivo: `be/alembic/versions/e1f2a3b4c5d6_seed_roles_and_permissions.py`

Se agregaron 3 módulos nuevos al catálogo de permisos:

| Módulo | Administrador | Capataz | Veterinario | Empleado |
|--------|:---:|:---:|:---:|:---:|
| `economica` | CRUD | CRUD | R | R |
| `reproductivo` | CRUD | CRUD | CRUD | R |
| `sanitario` | CRUD | CRUD | CRUD | R |

**Ejecución:** Se ejecuta automáticamente como parte de la migración.

---

## Endpoints de API

Base: `/api/v1/farms/{farm_id}/economics`

| Método | Ruta | Descripción | Permiso |
|--------|------|-------------|---------|
| `POST` | `/` | Crear movimiento económico | `economica.can_create` |
| `GET` | `/` | Listar movimientos (con filtros) | `economica.can_read` |
| `GET` | `/{record_id}` | Obtener movimiento por ID | `economica.can_read` |
| `PUT` | `/{record_id}` | Actualizar movimiento | `economica.can_update` |
| `DELETE` | `/{record_id}` | Eliminar movimiento (soft) | `economica.can_delete` |
| `GET` | `/indicators` | Indicadores económicos | `economica.can_read` |

### Filtros para GET `/`

- `record_type` — Filtrar por tipo (`ingreso` / `egreso`)
- `category` — Filtrar por categoría
- `date_from` — Fecha inicial (YYYY-MM-DD)
- `date_to` — Fecha final (YYYY-MM-DD)

### Indicadores (GET `/indicators`)

Respuesta `EconomicIndicators`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total_income` | number | Suma total de ingresos |
| `total_expense` | number | Suma total de egresos |
| `balance` | number | Diferencia (ingresos - egresos) |
| `income_by_category` | object | Desglose de ingresos por categoría |
| `expense_by_category` | object | Desglose de egresos por categoría |
| `monthly_income` | number | Ingresos del mes actual |
| `monthly_expense` | number | Egresos del mes actual |
| `monthly_balance` | number | Balance del mes actual |
| `avg_income_per_day` | number | Promedio diario de ingresos |
| `avg_expense_per_day` | number | Promedio diario de egresos |

**Soporta filtro por fecha:** `?date_from=2026-01-01&date_to=2026-06-15`

---

## Catálogo de Categorías

### Ingresos
| Categoría | Descripción |
|-----------|-------------|
| `venta_leche` | Venta de leche |
| `venta_animal` | Venta de animal |
| `venta_cria` | Venta de cría |
| `subsidio` | Subsidio gubernamental |
| `otro_ingreso` | Otro ingreso |

### Egresos
| Categoría | Descripción |
|-----------|-------------|
| `compra_insumo` | Compra de insumo |
| `compra_animal` | Compra de animal |
| `servicio_veterinario` | Servicio veterinario |
| `transporte` | Transporte |
| `personal` | Personal |
| `mantenimiento` | Mantenimiento |
| `impuesto` | Impuesto |
| `otro_gasto` | Otro gasto |

---

## Frontend: EconomicDashboard

**Ruta:** `/farms/:farmId/economics`
**Archivo:** `fe/src/pages/EconomicDashboard.tsx`
**API Client:** `fe/src/api/economics.ts`

### Componentes del Dashboard

1. **Filtros de fecha** — Selectores Desde/Hasta + botón Filtrar/Limpiar
2. **Tarjetas de resumen** — Total Ingresos, Total Egresos, Balance, Promedio diario
3. **Gráfico de ingresos por categoría** — BarChart horizontal (Recharts)
4. **Gráfico de egresos por categoría** — BarChart horizontal (Recharts)
5. **Gráfico de balance mensual** — LineChart con dos series (ingresos/egresos)

### Dependencias
- `recharts` — Gráficos (ya instalado)
- `lucide-react` — Iconos (ya instalado)

---

## Configuración de Rutas

En `fe/src/App.tsx` se agregó:

```tsx
<Route path="/farms/:farmId/economics" element={<EconomicDashboard />} />
```

En `fe/src/pages/FarmDetailPage.tsx` se agregó botón de navegación:
```tsx
<Link to={`/farms/${farmId}/economics`}>
  <BarChart3 size={16} />
  Económico
</Link>
```

---

## Pruebas

Para probar los endpoints manualmente:

```bash
# Crear un ingreso
curl -X POST http://localhost:8000/api/v1/farms/{farm_id}/economics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"record_type": "ingreso", "category": "venta_leche", "amount": 1500000, "record_date": "2026-06-15"}'

# Obtener indicadores
curl http://localhost:8000/api/v1/farms/{farm_id}/economics/indicators \
  -H "Authorization: Bearer {token}"

# Filtrar por fecha
curl "http://localhost:8000/api/v1/farms/{farm_id}/economics?date_from=2026-01-01&date_to=2026-06-15" \
  -H "Authorization: Bearer {token}"
```
