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
| **Equipo** | Tomas Canon, Edwin Delgado, Camilo Ortiz |
| **Roles Scrum** | Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer), Camilo Ortiz (Developer / Scrum Master) |

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint6-tomas` |
| Edwin | `feature/sprint6-edwin` |
| Camilo | `feature/sprint6-camilo` |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra registrar compras, ventas y traslados de animales con actualizacion automatica de estado (HU009), y consultar indicadores economicos por actividad (HU010).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU009 | Registrar ingresos y salidas de animales | Alta | 5 |
| HU010 | Registrar informacion economica | Alta | 5 |
| HU007 | Registrar desarrollo de terneros | Media | 5 |

**Total Story Points del Sprint: 15** (~45h estimadas)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] HU006 completada en Sprint 5 (modelo, CRUD, regla parto, auto-ternero, ReproductiveTimeline)
- [x] HU007: modelo `Calf` y endpoints de desarrollo de terneros implementados por Camilo
- [x] HU009: modelo `AnimalMovement` y estados de `Bovine` documentados antes de comenzar
- [x] HU010: categorias fijas de ingresos/egresos definidas
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU009 - Ingresos y Salidas de Animales — **Tomas** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 9.1 | Modelo `AnimalMovement` + migracion | Tomas | ✅ Hecho | 3h |
| 9.2 | CRUD de movimientos comerciales por finca | Tomas | ✅ Hecho | 4h |
| 9.3 | Regla de actualizacion automatica de estado del bovino | Tomas | ✅ Hecho | 2h |
| 9.4 | UI de movimientos por bovino/finca | Tomas | ✅ Hecho | 4h |

### HU010 - Informacion Economica — **Edwin** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 10.1 | Modelo de ingresos/egresos por actividad | Edwin | ✅ Hecho | 4h |
| 10.2 | Endpoints de registro y consulta economica | Edwin | ✅ Hecho | 3h |
| 10.3 | Indicadores: costos, ingresos, balance y promedios | Edwin | ✅ Hecho | 3h |
| 10.4 | Dashboard economico con filtros | Edwin | ✅ Hecho | 4h |

### HU007 - Desarrollo de Terneros — **Camilo** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 7.1 | Endpoint/vista de terneros por edad/estado | Camilo | ✅ Hecho | 3h |
| 7.2 | Registro de crecimiento (peso, alimentacion, estado) | Camilo | ✅ Hecho | 3h |
| 7.3 | Componente `CalfList` con indicadores de crecimiento | Camilo | ✅ Hecho | 4h |
| 7.4 | Curva de crecimiento del ternero (GrowthChart) | Camilo | ✅ Hecho | 4h |
| 7.5 | Integracion con ficha general del bovino | Camilo | ✅ Hecho | 2h |

---

## Definition of Done (DoD)

- [x] Registros economicos vinculados a actividad productiva
- [x] Indicadores economicos visibles y filtrables
- [x] Lista y curva de crecimiento de terneros funcional
- [x] Sin errores tecnicos en backend/frontend
- [x] Evidencia funcional y pruebas minimas (backend + frontend)
- [x] HU009 — Modelo AnimalMovement, CRUD, regla de estado automatica y UI completados

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Integridad entre movimiento y estado del animal | Media | Alto | Pruebas de transaccion y validacion cruzada |
| Clasificacion economica inconsistente | Media | Medio | Catalogo fijo de categorias y validacion |

---

## Sprint Review

**Fecha:** 26 de junio de 2026  
**Participantes:** Tomas Canon, Edwin Delgado, Camilo Ortiz

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| CRUD movimientos de animales (compra/venta/traslado) | ✅ Entregado | HU009 — Tomas |
| Actualizacion automatica de estado del bovino | ✅ Entregado | HU009 — Tomas |
| UI de movimientos por finca/bovino | ✅ Entregado | HU009 — Tomas |
| Modelo, endpoints e indicadores economicos (10.1-10.3) | ✅ Entregado | HU010 — Edwin |
| Dashboard economico con indicadores | ✅ Entregado | HU010.4 — Edwin |
| CRUD terneros, CalfList y GrowthChart (7.1-7.5) | ✅ Entregado | HU007 — Camilo |

### Story Points completados

HU009 (5 SP) + HU010 (10 SP) + HU007 (10 SP) = **25 SP completados**.

---

## Sprint Retrospectiva

### Que salio bien?

- HU007 completada por Camilo con backend completo, componentes frontend (CalfList, GrowthChart) y documentacion detallada
- HU010 completada por Edwin con modelo economico, endpoints CRUD, indicadores y dashboard visual con filtros
- Migracion a pyproject.toml, validacion de formularios y seed DANE completados por Tomas
- Sin conflictos mayores al integrar las 3 ramas de feature (HU007 + HU010)
- Camilo reincorporado al equipo con entrega sustancial

### Que se puede mejorar?

- Sincronizacion entre ramas: Tomas trabajo directamente en main sin usar feature branch, lo que dificulta el seguimiento por HU
- Documentacion de scripts (SPRINT_06_HU007_QUICKSTART.md, etc.) quedo en branch de feature y debe consolidarse en main

### Acciones para Sprint 7

- Confirmar que los modulos economicos exponen datos consumibles por HU013 (reportes)
- Definir estado de HU009: completar en Sprint 7 o redistribuir
- Unificar formato de documentacion de scripts siguiendo el estandar de SPRINT_06_HU007_QUICKSTART.md
- Revisar velocidad real del equipo vs 20 puntos planificados
