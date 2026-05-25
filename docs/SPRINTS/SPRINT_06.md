# SCRUM - Sprint 6
## BoviTrack · Terneros y Planificacion Sanitaria

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 6 |
| **Duracion** | 15 dias |
| **Fecha inicio** | 13 de junio de 2026 |
| **Fecha fin** | 26 de junio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Implementar seguimiento de terneros (HU007) y completar gestion sanitaria con planes, calendario y alertas (HU008).

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU007 | Registrar desarrollo de terneros | Media | 5 |
| HU008 (cierre) | Planificar y registrar actividades sanitarias | Alta | 8 |

**Total Story Points del Sprint: 13**

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

**Fecha:** 16 de junio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

Pendiente de ejecucion.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente.

### Que se puede mejorar?

Pendiente.
