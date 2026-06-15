# SCRUM - Sprint 6
## BoviTrack · Movimientos del Hato, Gestion Economica y Cierre Reproductivo

---

## Informacion General

| Campo | Valor |
|---|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 6 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 13 de junio de 2026 |
| **Fecha fin** | 26 de junio de 2026 |
| **Equipo** | Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer / Scrum Master) |

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint6-tomas` |
| Edwin | `feature/sprint6-edwin` |

> **Nota:** Camilo Ortiz salió del equipo al cierre del Sprint 5. Sus HU (HU007 - Desarrollo de Terneros) quedan sin asignar y se redistribuirán o aplazarán en Sprint 7.

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra registrar compras, ventas y traslados de animales con actualizacion automatica de estado (HU009), y consultar indicadores economicos por actividad (HU010).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~40h por sprint (2 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU009 | Registrar ingresos y salidas de animales | Alta | 5 |
| HU010 | Registrar informacion economica | Alta | 5 |
| HU007 | Registrar desarrollo de terneros | Media | 5 |

**Total Story Points del Sprint: 15** (~45h estimadas, dentro de la capacidad del equipo — HU006 cierre completado en Sprint 5)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] HU006 completada en Sprint 5 (modelo, CRUD, regla parto, auto-ternero, ReproductiveTimeline)
- [x] HU007: filtro de terneros por `birth_date` identificado sobre modelo `Bovine` existente
- [x] HU009: modelo `AnimalMovement` y estados de `Bovine` documentados antes de comenzar
- [x] HU010: categorias fijas de ingresos/egresos definidas
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU009 - Ingresos y Salidas de Animales — **Tomas** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 9.1 | Modelo `AnimalMovement` + migracion | Tomas | 🔲 Por hacer | 3h |
| 9.2 | CRUD de movimientos comerciales por finca | Tomas | 🔲 Por hacer | 4h |
| 9.3 | Regla de actualizacion automatica de estado del bovino | Tomas | 🔲 Por hacer | 2h |
| 9.4 | UI de movimientos por bovino/finca | Tomas | 🔲 Por hacer | 4h |

### HU010 - Informacion Economica — **Edwin** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 10.1 | Modelo de ingresos/egresos por actividad | Edwin | ✅ Hecho | 4h |
| 10.2 | Endpoints de registro y consulta economica | Edwin | ✅ Hecho | 3h |
| 10.3 | Indicadores: costos, ingresos, balance y promedios | Edwin | ✅ Hecho | 3h |
| 10.4 | Dashboard economico con filtros | Edwin | ✅ Hecho | 4h |

### HU007 - Desarrollo de Terneros — **Sin asignar** (Camilo fuera del equipo)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 7.1 | Endpoint/vista de terneros por edad/estado | — | ❌ Pendiente | 3h |
| 7.2 | Registro de crecimiento (peso, alimentacion, estado) | — | ❌ Pendiente | 3h |
| 7.3 | Componente `CalfList` con indicadores de crecimiento | — | ❌ Pendiente | 4h |
| 7.4 | Curva de crecimiento del ternero | — | ❌ Pendiente | 4h |
| 7.5 | Integracion con ficha general del bovino | — | ❌ Pendiente | 2h |

> **Impacto:** HU007 queda fuera del alcance de Sprint 6. Se redistribuirá en Sprint 7 o se aplazará.

---

## Definition of Done (DoD)

- [ ] Movimientos actualizan estado del animal correctamente
- [x] Registros economicos vinculados a actividad productiva
- [x] Indicadores visibles y filtrables
- [ ] Lista y curva de crecimiento de terneros funcional (HU007 — fuera de alcance)
- [ ] Sin errores tecnicos en backend/frontend
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Integridad entre movimiento y estado del animal | Media | Alto | Pruebas de transaccion y validacion cruzada |
| Clasificacion economica inconsistente | Media | Medio | Catalogo fijo de categorias y validacion |

---

## Sprint Review

**Fecha:** 26 de junio de 2026  
**Participantes:** Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| CRUD movimientos de animales (compra/venta/traslado) | 🔲 Pendiente | HU009 — Tomas |
| Actualizacion automatica de estado del bovino | 🔲 Pendiente | HU009 — Tomas |
| UI de movimientos por finca/bovino | 🔲 Pendiente | HU009 — Tomas |
| Modelo, endpoints e indicadores economicos (10.1-10.3) | ✅ Entregado | HU010 — Edwin |
| Dashboard economico con indicadores | ✅ Entregado | HU010.4 — Edwin |
| Lista y curva de crecimiento de terneros | ❌ Excluido | HU007 — fuera de alcance (Camilo fuera) |

### Story Points completados

Pendiente de cierre. HU010 backend completo (~10 SP), HU007 excluido (~5 SP).

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 7

- Confirmar que los modulos economicos exponen datos consumibles por HU013 (reportes)
- Revisar velocidad real del equipo vs 18 puntos planificados
