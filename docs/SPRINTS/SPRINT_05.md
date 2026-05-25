# SCRUM - Sprint 5
## BoviTrack · Cierre de Control Productivo y Reproductivo

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 5 |
| **Duracion** | 15 dias |
| **Fecha inicio** | 30 de mayo de 2026 |
| **Fecha fin** | 12 de junio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Cerrar HU005 con pesajes y visualizacion productiva por bovino, e implementar HU006 para seguimiento reproductivo completo (servicios, diagnosticos, partos y fechas estimadas).

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU005 (cierre) | Registrar alimentacion, ordenos y pesajes para control productivo | Alta | 8 |
| HU006 | Registrar control reproductivo para seguimiento veterinario | Alta | 8 |

**Total Story Points del Sprint: 16**

---

## Sprint Backlog

### HU005 - Alimentacion, Ordenos y Pesajes (cierre)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 5.1 | Modelo/tabla de pesajes historicos por bovino | Camilo | 🔲 Por hacer | 3h |
| 5.2 | Endpoint `POST /farms/{id}/bovines/{id}/weights` | Edwin | 🔲 Por hacer | 3h |
| 5.3 | Endpoint `GET /farms/{id}/bovines/{id}/weights` | Edwin | 🔲 Por hacer | 2h |
| 5.4 | Ajustes de filtros en `/food` por bovino/lote | Camilo | 🔲 Por hacer | 2h |
| 5.5 | Ajustes de filtros en `/milk-production` por bovino | Camilo | 🔲 Por hacer | 2h |
| 5.6 | Componente `WeightHistory` + integracion en `BovineDetailPage` | Tomas | 🔲 Por hacer | 4h |
| 5.7 | Grafica de evolucion (peso y ordeno) en detalle de bovino | Tomas | 🔲 Por hacer | 5h |

### HU006 - Control Reproductivo

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 6.1 | Modelo `ReproductiveEvent` + migracion Alembic | Edwin | 🔲 Por hacer | 4h |
| 6.2 | CRUD `reproductive-events` por bovino | Camilo | 🔲 Por hacer | 4h |
| 6.3 | Regla de fecha estimada de parto (+283 dias) | Camilo | 🔲 Por hacer | 2h |
| 6.4 | Generacion automatica de ternero al registrar parto | Edwin | 🔲 Por hacer | 4h |
| 6.5 | Componente `ReproductiveTimeline` | Tomas | 🔲 Por hacer | 4h |
| 6.6 | QA funcional y pruebas de regresion HU005/HU006 | Edwin | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

Un item se considera **Hecho** cuando cumple todos los criterios:

- [ ] Endpoints funcionando (200/201/204 segun corresponda)
- [ ] Validaciones de negocio y de datos implementadas
- [ ] Integracion frontend-backend completa
- [ ] No hay errores de TypeScript ni de imports Python
- [ ] Pruebas minimas ejecutadas para casos criticos
- [ ] Evidencia de demo registrada

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Logica de parto automatico con creacion de ternero | Media | Alto | Entregar primero CRUD reproductivo y luego automatismo |
| Falta de datos historicos para graficas | Media | Medio | Sembrar datos de prueba para demo |

---

## Sprint Review

**Fecha:** 1 de junio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

Pendiente de ejecucion.

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente.

### Que se puede mejorar?

Pendiente.
