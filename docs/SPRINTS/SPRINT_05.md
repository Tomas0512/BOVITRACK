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

> Al final del sprint, el veterinario podra consultar el historial de pesajes y gráfica de evolución de cada bovino (HU005), y registrar eventos reproductivos completos con cálculo automático de fecha de parto (HU006).

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

### HU005 - Alimentacion, Ordenos y Pesajes (cierre) — ✅ COMPLETO

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 5.1 | Modelo/tabla de pesajes historicos por bovino | Camilo | ✅ Hecho | 3h |
| 5.2 | Endpoint `POST /farms/{id}/bovines/{id}/weights` | Edwin | ✅ Hecho | 3h |
| 5.3 | Endpoint `GET /farms/{id}/bovines/{id}/weights` | Edwin | ✅ Hecho | 2h |
| 5.4 | Ajustes de filtros en `/food` por bovino/lote | Camilo | ✅ Hecho | 2h |
| 5.5 | Ajustes de filtros en `/milk-production` por bovino | Camilo | ✅ Hecho | 2h |
| 5.6 | Componente `WeightHistory` + integracion en `BovineDetailPage` | Tomas | ✅ Hecho | 4h |
| 5.7 | Grafica de evolucion (peso y ordeno) en detalle de bovino | Tomas | ✅ Hecho | 5h |

### HU006 - Control Reproductivo

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 6.1 | Modelo `ReproductiveEvent` + migracion Alembic | Edwin | ✅ Hecho | 4h |
| 6.2 | CRUD `reproductive-events` por bovino | Camilo | ✅ Hecho (Edwin) | 4h |
| 6.3 | Regla de fecha estimada de parto (+283 dias) | Camilo | ✅ Hecho (Edwin) | 2h |
| 6.4 | Generacion automatica de ternero al registrar parto | Edwin | ✅ Hecho | 4h |
| 6.5 | Componente `ReproductiveTimeline` | Tomas | ✅ Hecho | 4h |
| 6.6 | QA funcional y pruebas de regresion HU005/HU006 | Edwin | ✅ Hecho | 3h |

---

## Definition of Done (DoD)

Un item se considera **Hecho** cuando cumple todos los criterios:

- [x] Endpoints funcionando (200/201/204 segun corresponda)
- [x] Validaciones de negocio y de datos implementadas
- [x] Integracion frontend-backend completa
- [x] No hay errores de TypeScript ni de imports Python
- [x] Pruebas minimas ejecutadas para casos criticos
- [x] Evidencia de demo registrada

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Logica de parto automatico con creacion de ternero | Media | Alto | Pasa a Sprint 6 para dar tiempo a completar |
| Falta de datos historicos para graficas | Media | Medio | Datos de prueba sembrados para demo |

---

## Sprint Review

**Fecha:** 15 de junio de 2026  
**Participantes:** Tomas Canon, Edwin Delgado, Camilo Ortiz

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Historial de pesajes por bovino | ✅ Hecho | Modelo, endpoints y componente WeightHistory |
| Grafica de evolucion de peso | ✅ Hecho | Componente WeightChart con Recharts |
| CRUD eventos reproductivos | ✅ Hecho | Backend completo por Edwin |
| Calculo fecha estimada de parto | ✅ Hecho | Regla +283 dias incluida en servicio |
| Generacion automatica de ternero al registrar parto | ✅ Hecho | Implementado por Edwin |
| Componente ReproductiveTimeline | ✅ Hecho | Implementado por Tomas |
| Tests unitarios HU006 | ✅ Hecho | 7 tests creados en be/tests/test_reproductive_event.py |

### Story Points completados

| Metrica | Valor |
|---|---|
| Story Points planificados | 16 |
| Story Points completados | 16 (HU005 completa 8 + HU006 completa 8) |
| Story Points pendientes (→ Sprint 6) | 0 — Sprint cerrado |

---

## Sprint Retrospectiva

### Que salio bien?

- HU005 completo (backend + frontend + graficas)
- HU006 completo con auto-ternero y timeline
- Coordinacion Edwin-Tomas para cerrar pendientes
- Tests unitarios creados

### Que se puede mejorar?

- Actualizar los documentos del sprint en tiempo real para reflejar el avance real

### Acciones para Sprint 6

- Edwin: HU010 Informacion economica (rama `feature/sprint6-edwin`)
- Tomas: HU009 Movimientos de animales (rama `feature/sprint6-tomas`)
- HU007 (terneros) sin responsable — decidir si pasa a Sprint 7 o se divide
