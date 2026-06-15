# SCRUM - Sprint 6
## BoviTrack · Movimientos del Hato, Gestion Economica y Cierre Reproductivo

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 6 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 13 de junio de 2026 |
| **Fecha fin** | 26 de junio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint6-tomas` |
| Edwin | `feature/sprint6-edwin` |
| Camilo | `feature/sprint6-camilo` |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra registrar compras, ventas y traslados de animales con actualizacion automatica de estado (HU009), consultar indicadores economicos por actividad (HU010), y el veterinario podra completar el modulo reproductivo con generacion automatica de ternero y linea de tiempo (HU006 cierre) y consultar desarrollo de terneros (HU007).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU009 | Registrar ingresos y salidas de animales | Alta | 5 |
| HU010 | Registrar informacion economica | Alta | 5 |
| HU006 (cierre) | Completar control reproductivo (auto-ternero + timeline) | Alta | 3 |
| HU007 | Registrar desarrollo de terneros | Media | 5 |

**Total Story Points del Sprint: 18** (~54h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] HU006 backend completado en Sprint 5 (modelo, CRUD, regla parto). Pendientes: auto-ternero y frontend
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
| 10.1 | Modelo de ingresos/egresos por actividad | Edwin | 🔲 Por hacer | 4h |
| 10.2 | Endpoints de registro y consulta economica | Edwin | 🔲 Por hacer | 3h |
| 10.3 | Indicadores: costos, ingresos, balance y promedios | Edwin | 🔲 Por hacer | 3h |
| 10.4 | Dashboard economico con filtros | Edwin | 🔲 Por hacer | 4h |

### HU006 - Cierre Control Reproductivo — **Camilo**

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 6.4 | Generacion automatica de ternero al registrar parto | Camilo | 🔲 Por hacer | 4h |
| 6.5 | Componente `ReproductiveTimeline` | Camilo | 🔲 Por hacer | 4h |
| 6.6 | QA funcional HU006 | Camilo | 🔲 Por hacer | 2h |

### HU007 - Desarrollo de Terneros — **Camilo**

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 7.1 | Endpoint/vista de terneros por edad/estado | Camilo | 🔲 Por hacer | 3h |
| 7.2 | Registro de crecimiento (peso, alimentacion, estado) | Camilo | 🔲 Por hacer | 3h |
| 7.3 | Componente `CalfList` con indicadores de crecimiento | Camilo | 🔲 Por hacer | 4h |
| 7.4 | Curva de crecimiento del ternero | Camilo | 🔲 Por hacer | 4h |
| 7.5 | Integracion con ficha general del bovino | Camilo | 🔲 Por hacer | 2h |

---

## Definition of Done (DoD)

- [ ] Movimientos actualizan estado del animal correctamente
- [ ] Registros economicos vinculados a actividad productiva
- [ ] Indicadores visibles y filtrables
- [ ] Auto-generacion de ternero funcional al registrar parto
- [ ] ReproductiveTimeline visible en detalle del bovino
- [ ] Lista y curva de crecimiento de terneros funcional
- [ ] Sin errores tecnicos en backend/frontend
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Integridad entre movimiento y estado del animal | Media | Alto | Pruebas de transaccion y validacion cruzada |
| Clasificacion economica inconsistente | Media | Medio | Catalogo fijo de categorias y validacion |
| Camilo tiene 2 HU simultaneas (HU006 cierre + HU007) | Media | Medio | Son tareas pequenas (~22h total) |

---

## Sprint Review

**Fecha:** 26 de junio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| CRUD movimientos de animales (compra/venta/traslado) | 🔲 Pendiente | |
| Actualizacion automatica de estado del bovino | 🔲 Pendiente | |
| UI de movimientos por finca/bovino | 🔲 Pendiente | |
| Registro y consulta de ingresos/egresos | 🔲 Pendiente | |
| Dashboard economico con indicadores | 🔲 Pendiente | |
| Auto-generacion de ternero al registrar parto | 🔲 Pendiente | |
| ReproductiveTimeline | 🔲 Pendiente | |
| Lista y curva de crecimiento de terneros | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 7

- Confirmar que los modulos economicos exponen datos consumibles por HU013 (reportes)
- Revisar velocidad real del equipo vs 18 puntos planificados
