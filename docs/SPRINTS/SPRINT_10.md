# SCRUM - Sprint 10
## BoviTrack · Auditoria Avanzada y Operacion Offline

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 10 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 8 de agosto de 2026 |
| **Fecha fin** | 21 de agosto de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra filtrar y exportar el historial de auditoria por usuario, accion y fecha (HU015), y el usuario podra capturar datos sin conexion y sincronizarlos al recuperar conectividad con resolucion de conflictos (HU016). Este es el sprint de cierre del proyecto BoviTrack (HU001-HU016).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU015 (cierre) | Revisar auditorias del sistema | Alta | 5 |
| HU016 | Registrar datos sin conexion | Alta | 8 |

**Total Story Points del Sprint: 13** (~39h estimadas + tiempo de cierre y demo final del proyecto)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Estrategia de sincronizacion offline acordada (cola local + endpoint de sync)
- [x] Politica de resolucion de conflictos definida (last-write-wins o manual)
- [x] Auditoria existente revisada: filtros adicionales identificados vs lo ya construido
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU015 - Auditorias del Sistema (cierre)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 15.1 | Filtros avanzados (usuario, accion, fecha) en backend | Camilo | 🔲 Por hacer | 3h |
| 15.2 | Exportacion de auditoria filtrada | Edwin | 🔲 Por hacer | 3h |
| 15.3 | UI de auditoria con filtros y descarga | Tomas | 🔲 Por hacer | 4h |

### HU016 - Registro sin Conexion

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 16.1 | Cola local de operaciones offline | Tomas | 🔲 Por hacer | 4h |
| 16.2 | Endpoints de sincronizacion y versionado | Camilo | 🔲 Por hacer | 4h |
| 16.3 | Deteccion y manejo de conflictos de sincronizacion | Edwin | 🔲 Por hacer | 4h |
| 16.4 | UI de conflictos y resolucion | Tomas | 🔲 Por hacer | 3h |
| 16.5 | QA funcional HU015/HU016 + regresion final | Edwin | 🔲 Por hacer | 4h |

---

## Definition of Done (DoD)

- [ ] Auditoria exportable y filtrable
- [ ] Captura offline funcional con sincronizacion posterior
- [ ] Conflictos detectados y resolubles por usuario
- [ ] Sin errores tecnicos en backend/frontend
- [ ] Evidencia final de cierre HU001-HU016

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Complejidad de sincronizacion offline | Alta | Alto | Definir estrategia simple de versionado por registro |
| Conflictos frecuentes por edicion simultanea | Media | Alto | Politica clara de resolucion + trazabilidad |

---

## Sprint Review

**Fecha:** 21 de agosto de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Auditoria filtrable y exportable | 🔲 Pendiente | |
| Captura offline funcional | 🔲 Pendiente | |
| Sincronizacion al reconectar | 🔲 Pendiente | |
| Resolucion de conflictos por usuario | 🔲 Pendiente | |
| Evidencia final HU001-HU016 completa | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva — Cierre de Proyecto

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Lecciones aprendidas del proyecto (HU001-HU016)

- A completar en la retro final del sprint 10.
- Incluir: decisiones de arquitectura que funcionaron, estimaciones reales vs planificadas, recomendaciones para futuros proyectos.
