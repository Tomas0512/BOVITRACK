# SCRUM — Sprint 2
## BoviTrack · Frontend de Fincas, Lotes y Gestión de Potreros

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 2 |
| **Duración** | 2 semanas |
| **Fecha inicio** | 23 de marzo de 2026 |
| **Fecha fin** | 5 de abril de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner) |

---

## Objetivo del Sprint

> Completar la gestión de fincas y lotes con sus interfaces frontend (CRUD de lotes, páginas de detalle y creación de fincas) y construir el módulo completo de potreros y pasturas con validación de dependencia de lotes. Al final del sprint el usuario podrá gestionar fincas, lotes y potreros de extremo a extremo.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU002 (parcial) | Como Administrador quiero registrar fincas y lotes para organizar la estructura productiva — **tareas frontend: CRUD lotes, páginas y componentes** | Alta | 2 |
| HU003 | Como Capataz quiero gestionar potreros y pasturas para controlar su ocupación, descanso y rotación | Alta | 5 |

**Total Story Points del Sprint: 7**

---

## Sprint Backlog

### HU002 (parcial) — Fincas y Lotes: Frontend y CRUD de Lotes

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 2.5 | CRUD completo de lotes de tierra (`/farms/{id}/land-plots`) | Tomas | ✅ Hecho | 3h |
| 2.6 | Página `FarmDetailPage` con tarjetas de información de finca | Tomas | ✅ Hecho | 2h |
| 2.7 | Componentes `LandPlotList` y `LandPlotFormModal` | Tomas | ✅ Hecho | 3h |
| 2.8 | Página `CreateFarmPage` con selector dinámico de departamentos | Camilo | ✅ Hecho | 3h |

### HU003 — Potreros y Pasturas

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 3.1 | Modelo ORM `Paddock` con estado, cobertura y fechas de descanso | Camilo | ✅ Hecho | 2h |
| 3.2 | CRUD completo de potreros (`/farms/{id}/paddocks`) | Camilo | ✅ Hecho | 3h |
| 3.3 | Validación: solo se puede crear potrero si existe al menos un lote activo | Camilo | ✅ Hecho | 1h |
| 3.4 | Componente `PaddockList` con badges de estado y cobertura | Tomas | ✅ Hecho | 3h |
| 3.5 | Componente `PaddockFormModal` con fechas condicionales en estado "en descanso" | Tomas | ✅ Hecho | 3h |

---

## Definition of Done (DoD)

Un ítem se considera **Hecho** cuando cumple todos los criterios:

- [ ] El endpoint backend responde correctamente (200/201/204 según corresponda)
- [ ] Las validaciones Pydantic rechazan datos inválidos (422 con detalle)
- [ ] El componente frontend muestra y actualiza datos sin recargar la página
- [ ] No hay errores de TypeScript en el frontend
- [ ] No hay errores de importación en Python
- [ ] El código sigue el patrón del proyecto (router → service → model)
- [ ] Los permisos RBAC están aplicados en el endpoint correspondiente

---

## Sprint Review

**Fecha:** 5 de abril de 2026  
**Participantes:** Camilo Ortiz, Tomas Cañon

### Incremento entregado

| Módulo | Entregado | Observaciones |
|---|---|---|
| Gestión de lotes (LandPlot) | ✅ | CRUD + nombre único por finca |
| Página FarmDetailPage | ✅ | Tarjetas informativas de finca |
| Página CreateFarmPage | ✅ | Selector dinámico de departamentos |
| Componentes de lotes | ✅ | LandPlotList + LandPlotFormModal |
| Gestión de potreros | ✅ | CRUD + validación dependencia de lotes |
| Componentes de potreros | ✅ | PaddockList + PaddockFormModal |

### Story Points completados: 7 / 7 ✅

### Demo realizado:

1. Creación de finca con selector de departamento dinámico
2. Detalle de finca con tarjetas de información
3. CRUD de lotes con validación de nombre único
4. Registro de potrero → bloqueo si no hay lote activo
5. Gestión de estado de potrero con fechas de descanso

---

## Sprint Retrospectiva

### ¿Qué salió bien?

- Los endpoints backend de fincas ya estaban listos del Sprint 1, lo que aceleró la integración frontend.
- El patrón de componentes modales (`FormModal`) se consolidó y será reutilizable.
- La validación de dependencia de lotes previno inconsistencias en potreros.

### ¿Qué se puede mejorar?

- Los formularios del frontend comparten mucha lógica repetida (carga, error, submit). Se podría crear un hook `useFormState`.
- Los mensajes de error del backend no siempre llegan al frontend de forma legible.

### Acciones para el Sprint 3

- Reutilizar el patrón `FormModal` para los formularios de bovinos.
- Unificar el manejo de errores del frontend con un interceptor Axios global.
