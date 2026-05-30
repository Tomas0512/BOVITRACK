# SCRUM - Sprint 9
## BoviTrack · Reportes, Indicadores y Notificaciones

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

## Objetivo del Sprint

> Al final del sprint, el administrador podra generar y exportar reportes productivos, sanitarios y economicos con filtros por fecha (HU013), y el usuario podra configurar alertas automaticas y consultar su historial de notificaciones (HU014).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU013 (cierre) | Generar reportes e indicadores | Alta | 8 |
| HU014 | Recibir alertas y notificaciones | Media | 5 |

**Total Story Points del Sprint: 13** (~39h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Formatos de exportacion acordados (PDF y/o Excel)
- [x] Fuentes de datos de reportes identificadas (modulos HU005-HU012)
- [x] Canales de notificacion definidos (in-app y/o email)
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU013 - Reportes e Indicadores (cierre)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 13.1 | Completar filtros de reportes por fecha/categoria | Camilo | 🔲 Por hacer | 3h |
| 13.2 | Exportacion PDF/Excel | Edwin | 🔲 Por hacer | 4h |
| 13.3 | Pantalla de reportes con descarga | Tomas | 🔲 Por hacer | 4h |
| 13.4 | Ajustes de indicadores productivos/sanitarios/economicos | Camilo | 🔲 Por hacer | 3h |

### HU014 - Alertas y Notificaciones

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 14.1 | Motor de notificaciones por eventos proximos | Edwin | 🔲 Por hacer | 4h |
| 14.2 | Preferencias por canal y frecuencia | Camilo | 🔲 Por hacer | 3h |
| 14.3 | Historial de notificaciones enviadas | Edwin | 🔲 Por hacer | 3h |
| 14.4 | UI de configuracion de alertas + historial | Tomas | 🔲 Por hacer | 5h |
| 14.5 | QA funcional HU013/HU014 | Edwin | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

- [ ] Reportes exportables en formatos solicitados
- [ ] Indicadores visibles y con filtros funcionales
- [ ] Notificaciones configurables y registradas en historial
- [ ] Sin errores tecnicos en backend/frontend
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Fallas en generacion de archivos grandes | Media | Medio | Limitar rangos y paginar resultados |
| Notificaciones duplicadas o perdidas | Media | Alto | Idempotencia y trazabilidad de envios |

---

## Sprint Review

**Fecha:** 7 de agosto de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Reportes con filtros por fecha/categoria | 🔲 Pendiente | |
| Exportacion PDF/Excel funcional | 🔲 Pendiente | |
| Indicadores productivos/sanitarios/economicos | 🔲 Pendiente | |
| Motor de notificaciones por eventos proximos | 🔲 Pendiente | |
| Configuracion de alertas + historial | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 10

- Confirmar que la auditoria (HU015) puede reutilizar los filtros de reportes ya construidos.
- Definir la estrategia offline (HU016) antes de comenzar el sprint: PWA, Service Worker o app nativa.
