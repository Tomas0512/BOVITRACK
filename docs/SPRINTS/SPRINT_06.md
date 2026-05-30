# SCRUM - Sprint 6
## BoviTrack · Terneros y Planificacion Sanitaria

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

## Objetivo del Sprint

> Al final del sprint, el capataz podra consultar la lista de terneros con su curva de crecimiento (HU007), y el veterinario podra registrar planes sanitarios recurrentes y ver alertas de actividades proximas en los siguientes 7 dias (HU008).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU007 | Registrar desarrollo de terneros | Media | 5 |
| HU008 (cierre) | Planificar y registrar actividades sanitarias | Alta | 8 |

**Total Story Points del Sprint: 13** (~39h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Filtro de terneros por `birth_date` y estado identificado sobre el modelo `Bovine` existente
- [x] Modelo `SanitaryPlan` y logica de frecuencias documentada antes de comenzar
- [x] Dependencia con `Treatment` existente revisada para no duplicar logica
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU007 - Desarrollo de Terneros

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 7.1 | Endpoint/vista de terneros por edad/estado | Edwin | 🔲 Por hacer | 3h |
| 7.2 | Registro de crecimiento (peso, alimentacion, estado) | Camilo | 🔲 Por hacer | 3h |
| 7.3 | Componente `CalfList` con indicadores de crecimiento | Tomas | 🔲 Por hacer | 4h |
| 7.4 | Curva de crecimiento del ternero | Tomas | 🔲 Por hacer | 4h |
| 7.5 | Integracion con ficha general del bovino | Edwin | 🔲 Por hacer | 2h |

### HU008 - Actividades Sanitarias (cierre)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 8.1 | Modelo `SanitaryPlan` + migracion | Camilo | 🔲 Por hacer | 4h |
| 8.2 | CRUD `/sanitary-plans` + reglas de frecuencia | Edwin | 🔲 Por hacer | 4h |
| 8.3 | Endpoint de alertas sanitarias proximas | Camilo | 🔲 Por hacer | 3h |
| 8.4 | Calendario sanitario en frontend | Tomas | 🔲 Por hacer | 5h |
| 8.5 | Banner de alertas en `FarmDetailPage` | Edwin | 🔲 Por hacer | 2h |
| 8.6 | QA y pruebas de regresion HU007/HU008 | Edwin | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

- [ ] Endpoints y vistas funcionando segun criterios HU
- [ ] Alertas y calendario con fechas correctas
- [ ] Integracion completa en interfaz existente
- [ ] Sin errores de compilacion/lint
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Reglas de frecuencia sanitaria incompletas | Media | Alto | Iniciar con diaria/semanal/mensual y ampliar |
| Inconsistencias de datos historicos de terneros | Media | Medio | Definir validaciones y valores por defecto |

---

## Sprint Review

**Fecha:** 26 de junio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Vista y lista de terneros con indicadores | 🔲 Pendiente | |
| Curva de crecimiento del ternero | 🔲 Pendiente | |
| Modelo y CRUD de planes sanitarios | 🔲 Pendiente | |
| Endpoint de alertas sanitarias proximas | 🔲 Pendiente | |
| Banner de alertas en FarmDetailPage | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 7

- Verificar si las reglas de frecuencia sanitaria (diaria/semanal/mensual/anual) quedaron completas o requieren iteracion.
- Ajustar estimacion segun velocidad real registrada en Sprint 5 y 6.
