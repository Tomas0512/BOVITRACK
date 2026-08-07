# SCRUM - Sprint 9 (Cancelado / Absorbido)
## BoviTrack · Estabilizacion, QA Final y Preparacion de Cierre

> ## 📌 REPROGRAMACION — SPRINT ABSORBIDO
>
> **Este sprint ya NO se ejecuta como tal.** Debido a la fecha limite real del proyecto (23 de agosto de 2026), las actividades de estabilizacion, QA y preparacion de cierre fueron **absorbidas en el [Sprint 8 (Final)](./SPRINT_08.md)** (8–23 de agosto).
>
> **Mapeo de actividades reubicadas en Sprint 8:**
> | Actividad original (Sprint 9) | Dónde quedó |
> |---|---|
> | QA y pruebas de regresion HU001–HU013 | Tareas 16.1–16.5 (Edwin) |
> | Correccion de bugs | Tarea 16.6 (Edwin) + fixes propios de cada HU |
> | Revision de seguridad (OWASP) | Cubierta dentro del QA final (16.x) |
> | Optimizacion de rendimiento | Priorizada dentro de la correccion de bugs (16.6) |
> | Documentacion tecnica y de usuario | Tareas 16.8–16.9 (Edwin) |
>
> **El contenido siguiente queda como historial de la planificacion original.**

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 9 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 25 de julio de 2026 |
| **Fecha fin** | 7 de agosto de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint9-tomas` |
| Edwin | `feature/sprint9-edwin` |
| Camilo | `feature/sprint9-camilo` |

---

## Objetivo del Sprint

> Al final del sprint, el proyecto BoviTrack estara completamente funcional, libre de bugs criticos, con todos los modulos integrados y probados, listo para la demo final y despliegue. Este sprint no incluye nuevas HU, solo estabilizacion y aseguramiento de calidad.

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

No se incorporan nuevas HU en este sprint. El enfoque es 100% en calidad.

| Actividad | Prioridad | Horas estimadas |
|---|---|---|
| QA y pruebas de regresion HU001-HU016 | Alta | 24h |
| Correccion de bugs encontrados | Alta | 16h |
| Revision de seguridad (OWASP top 10) | Media | 8h |
| Optimizacion de rendimiento | Media | 8h |
| Documentacion tecnica y de usuario | Media | 10h |

**Total Horas Planificadas: ~66h** (dentro de la capacidad del equipo con margen)

---

## Definition of Ready (DoR)

Antes de iniciar el sprint de estabilizacion se verifica:

- [x] Todos los modulos HU001-HU016 tienen al menos su funcionalidad base implementada
- [x] Los sprints anteriores fueron cerrados formalmente
- [x] Se cuenta con un listado de bugs conocidos o riesgos tecnicos
- [x] Ambiente de pruebas disponible (local o staging)

---

## Sprint Backlog

### QA y Pruebas de Regresion

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 17.1 | Pruebas de regresion modulo auth (HU001) | Todos | 🔲 Por hacer | 4h |
| 17.2 | Pruebas de regresion fincas/potreros (HU002-HU003) | Todos | 🔲 Por hacer | 4h |
| 17.3 | Pruebas de regresion bovinos (HU004) | Todos | 🔲 Por hacer | 4h |
| 17.4 | Pruebas de regresion productivo (HU005) | Todos | 🔲 Por hacer | 4h |
| 17.5 | Pruebas de regresion reproductivo (HU006) | Todos | 🔲 Por hacer | 4h |
| 17.6 | Pruebas de regresion terneros (HU007) | Todos | 🔲 Por hacer | 3h |
| 17.7 | Pruebas de regresion sanitario (HU008) | Todos | 🔲 Por hacer | 3h |
| 17.8 | Pruebas de regresion movimientos (HU009) | Todos | 🔲 Por hacer | 3h |
| 17.9 | Pruebas de regresion economia (HU010) | Todos | 🔲 Por hacer | 3h |
| 17.10 | Pruebas de regresion inventarios (HU011) | Todos | 🔲 Por hacer | 3h |
| 17.11 | Pruebas de regresion documentos (HU012) | Todos | 🔲 Por hacer | 3h |
| 17.12 | Pruebas de regresion reportes (HU013) | Todos | 🔲 Por hacer | 3h |
| 17.13 | Pruebas de regresion notificaciones (HU014) | Todos | 🔲 Por hacer | 3h |
| 17.14 | Pruebas de regresion auditoria (HU015) | Todos | 🔲 Por hacer | 2h |
| 17.15 | Pruebas de regresion offline (HU016) | Todos | 🔲 Por hacer | 4h |

### Correccion de Bugs

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 18.1 | Correccion de bugs criticos encontrados en QA | Segun modulo | 🔲 Por hacer | 8h |
| 18.2 | Correccion de bugs medios/bajos | Segun modulo | 🔲 Por hacer | 8h |

### Seguridad, Rendimiento y Documentacion

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 19.1 | Revision OWASP top 10 (file upload, XSS, SQLi, auth) | Edwin | 🔲 Por hacer | 4h |
| 19.2 | Revision de rendimiento (consultas lentas, N+1) | Tomas | 🔲 Por hacer | 4h |
| 19.3 | Actualizar documentacion tecnica (README, API docs) | Camilo | 🔲 Por hacer | 4h |
| 19.4 | Preparar evidencias de cierre por modulo | Camilo | 🔲 Por hacer | 6h |

---

## Definition of Done (DoD)

- [ ] Todos los modulos HU001-HU016 probados y funcionales
- [ ] Sin bugs criticos ni altos conocidos
- [ ] Documentacion tecnica actualizada
- [ ] Evidencias de cierre preparadas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Bugs criticos que requieren reapertura de modulos | Media | Alto | Priorizar fixes sobre nuevas funcionalidades |
| Documentacion desactualizada | Alta | Medio | Dedicar tiempo especifico en el backlog |

---

## Sprint Review

**Fecha:** 7 de agosto de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Actividad | Entregado | Observaciones |
|---|---|---|
| Pruebas de regresion completas | 🔲 Pendiente | |
| Bugs correctivos aplicados | 🔲 Pendiente | |
| Revision de seguridad | 🔲 Pendiente | |
| Documentacion actualizada | 🔲 Pendiente | |

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 10

- Preparar demo final con todos los modulos
- Coordinar despliegue en produccion
- Completar retrospectiva final del proyecto
