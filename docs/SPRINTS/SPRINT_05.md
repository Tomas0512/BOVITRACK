# SCRUM - Sprint 5
## BoviTrack · Cierre de Control Productivo y Reproductivo

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 5 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 30 de mayo de 2026 |
| **Fecha fin** | 12 de junio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el veterinario podrá consultar el historial de pesajes y gráfica de evolución de cada bovino (HU005), y registrar eventos reproductivos completos con cálculo automático de fecha de parto (HU006).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU005 (cierre) | Registrar alimentacion, ordenos y pesajes para control productivo | Alta | 8 |
| HU006 | Registrar control reproductivo para seguimiento veterinario | Alta | 8 |

**Total Story Points del Sprint: 16** (~48h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verificó:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Modelos y tablas identificados (tabla `weights` pendiente de migracion)
- [x] Endpoints de referencia definidos en Postman
- [x] Dependencia con `Bovine` y `MilkProduction` existentes revisada
- [x] Libreria de graficas (Recharts) evaluada y disponible en el proyecto

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

**Fecha:** 12 de junio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Historial de pesajes por bovino | 🔲 Pendiente | |
| Grafica de evolucion de peso | 🔲 Pendiente | |
| CRUD eventos reproductivos | 🔲 Pendiente | |
| Calculo fecha estimada de parto | 🔲 Pendiente | |
| Generacion automatica de ternero al registrar parto | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 6

- Definir si la generacion automatica de ternero se entrega completa o como iteracion posterior.
- Revisar velocidad real del equipo vs 16 puntos planificados para ajustar Sprint 6.
