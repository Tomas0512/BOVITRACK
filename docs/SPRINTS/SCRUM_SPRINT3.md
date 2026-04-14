# SCRUM — Sprint 3
## BoviTrack · Registro y Administración de Animales

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 3 |
| **Duración** | 2 semanas |
| **Fecha inicio** | 6 de abril de 2026 |
| **Fecha fin** | 19 de abril de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner) |

---

## Objetivo del Sprint

> Construir el módulo completo de registro y administración de bovinos: modelo ORM con campos de raza, peso, entrada y trazabilidad de padres; CRUD con filtros; componentes frontend de listado, formulario y ficha individual; y la ruta de detalle por animal. Al final del sprint el usuario podrá gestionar el hato completo con trazabilidad individual.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU004 | Como Capataz quiero registrar y administrar animales para mantener la información del hato actualizada | Alta | 8 |

**Total Story Points del Sprint: 8**

---

## Sprint Backlog

### HU004 — Registro y Administración de Animales

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 4.1 | Modelo ORM `Bovine` con campos completos (raza, peso, entrada, padres) | Camilo | ✅ Hecho | 3h |
| 4.2 | CRUD completo de bovinos (`/farms/{id}/bovines`) con filtros | Camilo | ✅ Hecho | 4h |
| 4.3 | Componente `BovineList` con filtro por sexo y acciones | Tomas | ✅ Hecho | 3h |
| 4.4 | Componente `BovineFormModal` con todos los campos y selector de lote | Tomas | ✅ Hecho | 4h |
| 4.5 | Página `BovineDetailPage` con ficha individual y trazabilidad | Tomas | ✅ Hecho | 4h |
| 4.6 | Ruta `/farms/:farmId/bovines/:bovineId` registrada en `App.tsx` | Tomas | ✅ Hecho | 1h |

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

**Fecha:** 19 de abril de 2026  
**Participantes:** Camilo Ortiz, Tomas Cañon

### Incremento entregado

| Módulo | Entregado | Observaciones |
|---|---|---|
| Modelo ORM Bovine | ✅ | Campos completos: raza, peso, entrada, padres |
| CRUD de bovinos | ✅ | Endpoints con filtros por sexo y estado |
| Componente BovineList | ✅ | Listado con filtros y acciones rápidas |
| Componente BovineFormModal | ✅ | Formulario completo con selector de lote |
| Página BovineDetailPage | ✅ | Ficha individual con trazabilidad de padres |
| Ruta de detalle | ✅ | `/farms/:farmId/bovines/:bovineId` registrada |

### Story Points completados: 8 / 8 ✅

### Demo realizado:

1. Registro de bovino con todos los campos (raza, peso, fecha de entrada)
2. Listado de bovinos con filtro por sexo
3. Ficha individual del bovino con datos de trazabilidad
4. Selector de lote en el formulario de registro
5. Navegación completa: finca → bovinos → detalle individual

---

## Sprint Retrospectiva

### ¿Qué salió bien?

- La arquitectura modular permitió agregar el módulo de bovinos sin tocar los módulos anteriores.
- El patrón `FormModal` establecido en Sprint 2 se reutilizó exitosamente en `BovineFormModal`.
- Los cuatro módulos principales del sistema (usuarios, fincas, potreros, bovinos) están funcionales de extremo a extremo.

### ¿Qué se puede mejorar?

- Los formularios del frontend comparten mucha lógica repetida. Se debería crear un hook `useFormState`.
- Faltan pruebas unitarias para los servicios del backend.
- Los mensajes de error del backend no siempre llegan al frontend de forma legible.

### Acciones para el Sprint 4

- Unificar el manejo de errores del frontend con un interceptor Axios global.
- Agregar al menos pruebas básicas para los servicios críticos (auth, bovinos).
- Crear un componente reutilizable `FormField` para reducir repetición en modales.
