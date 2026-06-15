# SCRUM - Sprint 8
## BoviTrack · Notificaciones, Auditoria y Modo Offline

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 8 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 11 de julio de 2026 |
| **Fecha fin** | 24 de julio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el usuario podra configurar alertas automaticas y consultar su historial de notificaciones (HU014), el administrador podra filtrar y exportar el historial de auditoria por usuario, accion y fecha (HU015 cierre), y el usuario podra capturar datos sin conexion y sincronizarlos al recuperar conectividad (HU016).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU014 | Recibir alertas y notificaciones | Media | 5 |
| HU015 (cierre) | Revisar auditorias del sistema | Alta | 5 |
| HU016 | Registrar datos sin conexion | Alta | 8 |

**Total Story Points del Sprint: 18** (~54h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Canales de notificacion definidos (in-app y/o email)
- [x] Auditoria existente revisada: filtros adicionales identificados vs lo ya construido
- [x] Estrategia de sincronizacion offline acordada (cola local + endpoint de sync)
- [x] Politica de resolucion de conflictos definida (last-write-wins o manual)
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU014 - Alertas y Notificaciones — **Tomas** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 14.1 | Motor de notificaciones por eventos proximos | Tomas | 🔲 Por hacer | 4h |
| 14.2 | Preferencias por canal y frecuencia | Tomas | 🔲 Por hacer | 3h |
| 14.3 | Historial de notificaciones enviadas | Tomas | 🔲 Por hacer | 3h |
| 14.4 | UI de configuracion de alertas + historial | Tomas | 🔲 Por hacer | 5h |

### HU016 - Registro sin Conexion — **Edwin** (backend) + **Camilo** (frontend)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 16.1 | Cola local de operaciones offline | Edwin | 🔲 Por hacer | 4h |
| 16.2 | Endpoints de sincronizacion y versionado | Edwin | 🔲 Por hacer | 4h |
| 16.3 | Deteccion y manejo de conflictos de sincronizacion | Edwin | 🔲 Por hacer | 4h |
| 16.4 | UI de conflictos y resolucion | Camilo | 🔲 Por hacer | 3h |

### HU015 - Auditorias del Sistema (cierre) — **Camilo**

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 15.1 | Filtros avanzados (usuario, accion, fecha) en backend | Camilo | 🔲 Por hacer | 3h |
| 15.2 | Exportacion de auditoria filtrada | Camilo | 🔲 Por hacer | 3h |
| 15.3 | UI de auditoria con filtros y descarga | Camilo | 🔲 Por hacer | 4h |
| 15.4 | QA funcional HU014/HU015/HU016 | Camilo | 🔲 Por hacer | 4h |

---

## Definition of Done (DoD)

- [ ] Notificaciones configurables y registradas en historial
- [ ] Auditoria exportable y filtrable
- [ ] Captura offline funcional con sincronizacion posterior
- [ ] Conflictos detectados y resolubles por usuario
- [ ] Sin errores tecnicos en backend/frontend
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Complejidad de sincronizacion offline | Alta | Alto | Definir estrategia simple de versionado por registro |
| Conflictos frecuentes por edicion simultanea | Media | Alto | Politica clara de resolucion + trazabilidad |
| Notificaciones duplicadas o perdidas | Media | Alto | Idempotencia y trazabilidad de envios |

---

## Sprint Review

**Fecha:** 24 de julio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Motor de notificaciones por eventos proximos | 🔲 Pendiente | |
| Configuracion de alertas + historial | 🔲 Pendiente | |
| Auditoria filtrable y exportable | 🔲 Pendiente | |
| Captura offline funcional | 🔲 Pendiente | |
| Sincronizacion al reconectar | 🔲 Pendiente | |
| Resolucion de conflictos por usuario | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 9

- Evaluar si falta algo para el cierre final del proyecto
- Preparar demo final con todos los modulos integrados
