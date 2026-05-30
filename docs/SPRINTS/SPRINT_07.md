# SCRUM - Sprint 7
## BoviTrack · Movimientos del Hato y Gestion Economica

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 7 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 27 de junio de 2026 |
| **Fecha fin** | 10 de julio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra registrar compras, ventas y traslados de animales con actualizacion automatica de estado del bovino (HU009), y consultar indicadores de costos e ingresos por actividad productiva (HU010).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU009 | Registrar ingresos y salidas de animales | Alta | 5 |
| HU010 | Registrar informacion economica | Alta | 5 |

**Total Story Points del Sprint: 10** (~30h estimadas, holgura para QA y ajustes)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Modelo `AnimalMovement` y estados de `Bovine` documentados antes de comenzar
- [x] Categorias fijas de ingresos/egresos definidas (no dinamicas)
- [x] Dependencia con estado actual de `Bovine.status` revisada
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU009 - Ingresos y Salidas de Animales

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 9.1 | Modelo `AnimalMovement` + migracion | Camilo | 🔲 Por hacer | 4h |
| 9.2 | CRUD de movimientos comerciales por finca | Edwin | 🔲 Por hacer | 4h |
| 9.3 | Regla de actualizacion automatica de estado del bovino | Camilo | 🔲 Por hacer | 2h |
| 9.4 | UI de movimientos por bovino/finca | Tomas | 🔲 Por hacer | 4h |

### HU010 - Informacion Economica

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 10.1 | Modelo de ingresos/egresos por actividad | Edwin | 🔲 Por hacer | 4h |
| 10.2 | Endpoints de registro y consulta economica | Camilo | 🔲 Por hacer | 3h |
| 10.3 | Indicadores: costos, ingresos, balance y promedios | Camilo | 🔲 Por hacer | 3h |
| 10.4 | Dashboard economico con filtros | Tomas | 🔲 Por hacer | 4h |
| 10.5 | QA funcional HU009/HU010 | Edwin | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

- [ ] Movimientos actualizan estado del animal correctamente
- [ ] Registros economicos vinculados a actividad productiva
- [ ] Indicadores visibles y filtrables
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

**Fecha:** 10 de julio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| CRUD movimientos de animales (compra/venta/traslado) | 🔲 Pendiente | |
| Actualizacion automatica de estado del bovino | 🔲 Pendiente | |
| UI de movimientos por finca/bovino | 🔲 Pendiente | |
| Registro y consulta de ingresos/egresos | 🔲 Pendiente | |
| Dashboard economico con indicadores | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 8

- Confirmar que el catalogo de categorias economicas es suficiente para HU013 (reportes).
- Revisar si HU011 (inventarios) tiene dependencias con lo construido en HU010.
