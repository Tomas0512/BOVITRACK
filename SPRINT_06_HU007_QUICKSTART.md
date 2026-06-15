# 🚀 QUICK START: HU007 - Desarrollo de Terneros

## 👨‍💻 Para Camilo Ortiz

Has implementado exitosamente la **Historia de Usuario HU007** con todas sus tareas.  
Este documento te muestra dónde está cada cosa y cómo funciona.

---

## 📁 Archivos Que Creaste

### Backend (5 archivos)

| Archivo | Líneas | Propósito |
|---------|--------|----------|
| `be/app/services/calf_service.py` | 600+ | Lógica de terneros |
| `be/app/routers/calves.py` | 400+ | Endpoints HTTP |
| `be/app/schemas/calf.py` | 300+ | Validación Pydantic |
| `be/app/main.py` (modificado) | 2 líneas | Registrar router |

### Frontend (3 archivos)

| Archivo | Líneas | Propósito |
|---------|--------|----------|
| `fe/src/api/calves.ts` | 300+ | Cliente HTTP + tipos |
| `fe/src/components/calves/CalfList.tsx` | 600+ | Lista de terneros |
| `fe/src/components/calves/GrowthChart.tsx` | 400+ | Gráfica de crecimiento |

### Documentación (2 archivos)

| Archivo | Propósito |
|---------|----------|
| `docs/SPRINT_06_HU007_IMPLEMENTATION.md` | Documentación técnica completa |
| `SPRINT_06_HU007_QUICKSTART.md` | Este archivo |

---

## 🔧 Cómo Está Organizado

### BACKEND: La Estructura

```
be/app/
├── main.py                           ← Agregaste import + router
├── config.py                         ← No cambió
├── services/
│   ├── calf_service.py              ← ✨ NUEVO
│   └── other_service.py             ← Otros servicios
├── routers/
│   ├── calves.py                    ← ✨ NUEVO
│   └── other_router.py              ← Otros routers
└── schemas/
    ├── calf.py                      ← ✨ NUEVO
    └── other_schema.py              ← Otros schemas
```

### FRONTEND: La Estructura

```
fe/src/
├── api/
│   ├── calves.ts                    ← ✨ NUEVO
│   └── other.ts                     ← Otros clientes
└── components/
    ├── calves/                      ← ✨ NUEVA CARPETA
    │   ├── CalfList.tsx            ← ✨ NUEVO
    │   └── GrowthChart.tsx          ← ✨ NUEVO
    └── other/
```

---

## 💡 Cómo Funciona (Alto Nivel)

```
┌─────────────────┐
│   Frontend      │
│   React         │
├─────────────────┤
│  CalfList.tsx   │ ← Lista + tabla + modal
│  GrowthChart.tsx│ ← Gráfica de crecimiento
└────────┬────────┘
         │
         │ HTTP + JWT
         ↓
┌─────────────────────────────────────┐
│  Backend (FastAPI)                  │
├─────────────────────────────────────┤
│  routers/calves.py                  │ ← Endpoints
│  - GET  /calves                     │
│  - GET  /calves/{id}                │
│  - POST /calves/{id}/weights        │
│  - GET  /calves/{id}/weights        │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  services/calf_service.py           │
├─────────────────────────────────────┤
│  list_calves()                      │ ← Lógica
│  get_calf_details()                 │
│  record_calf_weight()               │
│  _calculate_growth_metrics()        │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────┐
│  PostgreSQL     │
│  - bovine       │
│  - weight       │
└─────────────────┘
```

---

## 📱 Cómo Usar en el Frontend

### Paso 1: Importar el componente

```tsx
// En tu página o dashboard
import CalfList from "@/components/calves/CalfList";
import GrowthChart from "@/components/calves/GrowthChart";

export function DashboardPage() {
  const farmId = "uuid-de-tu-finca";
  
  return (
    <div>
      {/* Lista de terneros */}
      <CalfList farmId={farmId} />
      
      {/* Gráfica de un ternero específico */}
      <GrowthChart 
        farmId={farmId}
        bovineId="uuid-del-ternero"
        calfName="Estrella"
        calfBreed="Brahman"
      />
    </div>
  );
}
```

### Paso 2: Qué Hace CalfList

```
┌────────────────────────────┐
│  📋 LISTA DE TERNEROS     │
├────────────────────────────┤
│  Filtros por edad:         │
│  [Todos] [0-30d] [31-90d]  │
│  [91-365d]                 │
├────────────────────────────┤
│  📊 Resumen Global:        │
│  Total: 12  |  Promedio: 95.5kg
├────────────────────────────┤
│  Tabla:                    │
│  ID | Nombre | Edad | Peso│
│  ... (filas con botón      │
│       "Pesar")             │
├────────────────────────────┤
│  🆙 Modal de Pesaje:       │
│  [Peso] [Fecha]            │
│  [Condición] [Notas]       │
│  [Guardar] [Cancelar]      │
└────────────────────────────┘
```

### Paso 3: Qué Hace GrowthChart

```
┌────────────────────────────────┐
│ 📊 CURVA DE CRECIMIENTO        │
├────────────────────────────────┤
│ Controles:                     │
│ [30d] [3m] [6m] [1año]        │
├────────────────────────────────┤
│ Gráfica:                       │
│ Kg │       ╱─────╲            │
│    │      ╱       ╲  ← Azul   │
│    │    ╱           ╲         │
│    │  ╱               ╲       │
│    └──────────────────────    │
│         Peso Actual (kg)      │
├────────────────────────────────┤
│ Estadísticas:                  │
│ Inicial: 35kg | Actual: 55kg  │
│ Ganancia: 20kg                │
└────────────────────────────────┘
```

---

## 🔌 Cómo Usar el API (si necesitas desde otro lugar)

### Importar funciones

```typescript
import { 
  listCalves, 
  getCalfDetails, 
  recordCalfWeight,
  getCalfWeightHistory
} from "@/api/calves";

// Listar terneros
const calves = await listCalves(farmId, 365, 0);

// Registrar pesaje
const weight = await recordCalfWeight(
  farmId, 
  bovineId,
  {
    weight_kg: 45.5,
    measured_date: "2026-06-15",
    body_condition: 3,
    observations: "Ganancia normal"
  }
);

// Obtener historial
const history = await getCalfWeightHistory(farmId, bovineId, 365);

// Obtener detalles
const detail = await getCalfDetails(farmId, bovineId);
```

---

## 🛠️ Explicación: Cada Servicio (Backend)

### calf_service.py: Las 4 Funciones Clave

#### 1️⃣ `list_calves()`
**¿Qué?** Lista terneros de una finca  
**¿Cuándo?** Al cargar CalfList  
**Parámetros:**
- `max_age_days`: Edad máxima (default 365)
- `min_age_days`: Edad mínima (default 0)
- `status_filter`: Estado (opcional)

**Retorna:** Lista de bovinos que son terneros

**Ejemplo:**
```python
# Terneros entre 30 y 90 días
calves = list_calves(db, farm_id, max_age_days=90, min_age_days=30)
```

#### 2️⃣ `record_calf_weight()`
**¿Qué?** Registra un pesaje nuevo  
**¿Cuándo?** Al presionar "Guardar" en el modal  
**Calcula automáticamente:**
- `daily_gain`: (peso actual - peso anterior) / días
- Actualiza `bovine.current_weight`
- Registra en auditoría

**Ejemplo:**
```python
weight = record_calf_weight(
  db, farm_id, bovine_id,
  weight_kg=Decimal("45.5"),
  measured_date=date(2026, 6, 15),
  body_condition=3,
  user_id=current_user.id
)
```

#### 3️⃣ `get_calf_weight_history()`
**¿Qué?** Obtiene todos los pesajes (para la gráfica)  
**¿Cuándo?** Al cargar GrowthChart  
**Retorna:** Array `[{date, weight_kg, daily_gain_kg}, ...]`

**Ejemplo:**
```python
history = get_calf_weight_history(db, farm_id, bovine_id, days_back=365)
# [{date: "2026-05-15", weight_kg: 40.0, daily_gain_kg: 0.2}, ...]
```

#### 4️⃣ `get_calf_summary_by_farm()`
**¿Qué?** Resumen global de terneros  
**¿Cuándo?** Al cargar CalfList  
**Retorna:**
```python
{
  "total_calves": 12,
  "calves_0_30_days": 2,
  "calves_31_90_days": 4,
  "calves_91_365_days": 6,
  "average_weight_kg": 95.5,
  "average_daily_gain": 0.65
}
```

---

## 📊 Explicación: Cálculos Automáticos

### 1. Ganancia Diaria (daily_gain)

```python
# Fórmula:
daily_gain = (peso_actual - peso_anterior) / días_entre_pesajes

# Ejemplo:
# Pesaje 1 (15 de mayo): 40 kg
# Pesaje 2 (30 de mayo): 48 kg
# Días transcurridos: 15
daily_gain = (48 - 40) / 15 = 0.53 kg/día
```

### 2. Peso Esperado (por raza y edad)

```python
# Tabla de referencia:
# Brahman: 0d=30kg, 30d=45kg, 60d=70kg, 90d=95kg, 365d=350kg
#
# Si el ternero tiene 45 días y es Brahman:
# expected = interpolación entre (30d=45kg) y (60d=70kg)
# expected = 45 + (45-30)/(60-30) * (70-45) = 45 + 12.5 = 57.5 kg
```

### 3. Porcentaje de Crecimiento

```python
# Fórmula:
percentage = (peso_actual / peso_esperado) × 100

# Ejemplo:
# Peso actual: 50 kg
# Peso esperado: 57.5 kg
# Percentage = (50 / 57.5) × 100 = 87%
```

### 4. Plan de Alimentación (Automático)

```python
0-30 días:    "Leche materna exclusiva + agua y sal"
31-60 días:   "Leche materna + introducir concentrado (500g/día)"
61-120 días:  "Leche + concentrado (1-2kg/día) + forraje"
121-180 días: "Destete gradual + concentrado (2-3kg/día) + forraje"
181-365 días: "Destete completo + concentrado (3kg/día) + forraje"
```

---

## ✅ Cómo Probar

### Backend (Terminal)

```bash
# 1. Inicia el servidor
cd be
python -m uvicorn app.main:app --reload

# 2. Prueba en otro terminal
# Listar terneros
curl -H "Authorization: Bearer <tu-token>" \
  http://localhost:8000/api/v1/farms/farm-uuid/calves

# 3. En Swagger UI
# http://localhost:8000/docs
# Busca "Terneros (HU007)" en la documentación
```

### Frontend (Browser)

```bash
# 1. Inicia el frontend
cd fe
pnpm dev

# 2. Navega a tu página/componente
# Deberías ver la lista de terneros

# 3. Prueba funcionalidades:
#    - Cambiar filtros por edad
#    - Presionar botón "Pesar"
#    - Llenar formulario y guardar
#    - Ver gráfica actualizada
```

---

## 🐛 Errores Comunes (y Soluciones)

### Error: "Ternero no encontrado"
**Causa:** Bovino no existe o no es ternero  
**Solución:** Verifica que:
- El bovine_id es correcto
- El bovino tiene menos de 365 días
- El bovino está activo (is_active=True)

### Error: "No tienes permiso"
**Causa:** Falta RBAC "can_read" en bovines  
**Solución:** 
- Verifica que tu rol tiene permiso en bovines
- Verifica que perteneces a la finca

### Error: "Peso debe ser > 0"
**Causa:** Validación Pydantic rechaza weight_kg <= 0  
**Solución:** 
- Ingresa un peso positivo
- En decimal (45.5, no 45,5)

### Gráfica no carga
**Causa:** Pocas pesajes registrados  
**Solución:**
- Registra al menos 2 pesajes
- Espera a que se recargue

---

## 🎓 Lecciones Clave (Para Futuros Sprints)

### Lo que hiciste bien:

✅ **Comentarios exhaustivos:**
- Cada función tiene "¿Qué?", "¿Para qué?", "¿Impacto?"
- Cualquiera puede entender el código

✅ **Separación de capas:**
- Services: lógica pura
- Routers: HTTP solo
- Schemas: validación

✅ **Cálculos automáticos:**
- daily_gain se calcula sin que el usuario lo pida
- current_weight se actualiza sin intervención

✅ **Type safety:**
- TypeScript en frontend
- Type hints en Python
- Validación Pydantic

### Para mejorar:

⚠️ **Testing:** Crea tests unitarios para:
```bash
be/app/tests/test_calf_service.py
fe/src/components/calves/__tests__/CalfList.test.tsx
```

⚠️ **Integración:** Conecta con:
- BovineDetailPage (mostrar ternero específico)
- HU010 (costos de alimentación)
- HU013 (reportes con terneros)

---

## 📞 Referencia Rápida

| Necesito... | Ir a... | Función |
|------------|---------|---------|
| Listar terneros | API | `listCalves()` |
| Ver detalles + métricas | API | `getCalfDetails()` |
| Registrar pesaje | API | `recordCalfWeight()` |
| Ver gráfica | Componente | `<GrowthChart />` |
| Cambiar lógica de cálculos | Service | `calf_service.py` |
| Cambiar endpoints | Router | `calves.py` |
| Cambiar validación | Schema | `calf.py` |
| Cambiar UI | Componente | `CalfList.tsx` |

---

## 🎉 Felicidades!

Has completado exitosamente **HU007** con:

✅ 5 tareas (7.1 a 7.5)  
✅ 2,500+ líneas de código  
✅ Comentarios exhaustivos  
✅ Type safety (TS + Python)  
✅ RBAC implementado  
✅ Cálculos automáticos  
✅ UI/UX responsiva  
✅ Listo para testing  

**El siguiente paso:** Testing + Integración en Sprint 7.

---

**Creado para:** Camilo Ortiz  
**Sprint:** 6  
**Historia:** HU007 - Desarrollo de Terneros  
**Fecha:** 15 de Junio de 2026
