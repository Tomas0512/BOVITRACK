# SCRUM — Sprint 1
## BoviTrack · Gestión de Usuarios, Fincas, Animales y Estructura Productiva

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 1 |
| **Duración** | 4 semanas |
| **Fecha inicio** | 9 de marzo de 2026 |
| **Fecha fin** | 5 de abril de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner) |

---

## Objetivo del Sprint

> Construir el núcleo del sistema: autenticación segura de usuarios, gestión de fincas y lotes, administración de empleados con RBAC, registro de potreros y bovinos, y auditoría de accesos. Al final del sprint el sistema debe ser funcional de extremo a extremo para los cuatro módulos principales.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU001 | Como Administrador quiero generar usuarios, roles y accesos para controlar quién puede entrar al sistema | Alta | 8 |
| HU002 | Como Administrador quiero registrar fincas y lotes para organizar la estructura productiva | Alta | 5 |
| HU003 | Como Capataz quiero gestionar potreros y pasturas para controlar su ocupación, descanso y rotación | Alta | 5 |
| HU004 | Como Capataz quiero registrar y administrar animales para mantener la información del hato actualizada | Alta | 8 |

**Total Story Points del Sprint: 26**

---

## Sprint Backlog

### HU001 — Usuarios, Roles y Accesos

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 1.1 | Modelo ORM `User` con campos completos (documento, teléfono, nombre) | Camilo | ✅ Hecho | 2h |
| 1.2 | Endpoints de registro con validaciones Pydantic | Camilo | ✅ Hecho | 3h |
| 1.3 | Autenticación JWT (access + refresh token) | Camilo | ✅ Hecho | 4h |
| 1.4 | Flujo de recuperación de contraseña por correo | Tomas | ✅ Hecho | 3h |
| 1.5 | Restablecimiento de contraseña con token temporal | Tomas | ✅ Hecho | 2h |
| 1.6 | Sistema RBAC: modelos `Role` y `Permission` con 4 roles y 32 permisos | Camilo | ✅ Hecho | 5h |
| 1.7 | Dependencia `require_permission(module, action)` para proteger endpoints | Camilo | ✅ Hecho | 3h |
| 1.8 | Módulo de empleados: asignar, modificar y retirar roles en una finca | Tomas | ✅ Hecho | 4h |
| 1.9 | Historial de auditoría: endpoint y componente frontend | Tomas | ✅ Hecho | 3h |
| 1.10 | Páginas frontend: Register, Login, ForgotPassword, ResetPassword | Tomas | ✅ Hecho | 5h |

### HU002 — Fincas y Lotes

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 2.1 | Modelo ORM `Farm` con campos (nombre, área, departamento, teléfono) | Camilo | ✅ Hecho | 2h |
| 2.2 | Migración Alembic con seed de 33 departamentos de Colombia (códigos DANE) | Camilo | ✅ Hecho | 3h |
| 2.3 | CRUD completo de fincas (`GET /farms`, `POST`, `PUT`, `DELETE`) | Camilo | ✅ Hecho | 4h |
| 2.4 | Modelo ORM `LandPlot` con validación de nombre único por finca | Tomas | ✅ Hecho | 2h |
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

**Fecha:** 5 de abril de 2026  
**Participantes:** Camilo Ortiz, Tomas Cañon

### Incremento entregado

| Módulo | Entregado | Observaciones |
|---|---|---|
| Autenticación completa | ✅ | Register, Login, ForgotPassword, ResetPassword |
| RBAC (4 roles, 32 permisos) | ✅ | Administrador, Capataz, Veterinario, Empleado |
| Gestión de fincas | ✅ | CRUD + departamentos Colombia |
| Gestión de lotes (LandPlot) | ✅ | CRUD + nombre único por finca |
| Gestión de potreros | ✅ | CRUD + validación dependencia de lotes |
| Gestión de bovinos | ✅ | CRUD + ficha individual + trazabilidad |
| Módulo de empleados | ✅ | Asignar/modificar/retirar roles en finca |
| Historial de auditoría | ✅ | Componente colapsable en detalle de finca |

### Story Points completados: 26 / 26 ✅

### Demo realizado:

1. Registro de usuario → auto-login → dashboard
2. Creación de finca con departamento dinámico
3. Registro de lote → bloqueo de potrero si no hay lote
4. Registro de potrero con fechas de descanso
5. Registro de bovino → ficha individual con trazabilidad
6. Asignación de rol a empleado en la finca

---

## Sprint Retrospectiva

### ¿Qué salió bien?

- La arquitectura modular (router → service → model) permitió agregar módulos sin romper lo existente.
- El sistema RBAC centralizado con `require_permission` simplificó la protección de todos los endpoints.
- Las migraciones Alembic secuenciales mantuvieron la base de datos versionada y reproducible.

### ¿Qué se puede mejorar?

- Los formularios del frontend comparten mucha lógica repetida (carga, error, submit). Se podría crear un hook `useFormState`.
- Faltan pruebas unitarias para los servicios del backend.
- Los mensajes de error del backend no siempre llegan al frontend de forma legible.

### Acciones para el Sprint 2

- Unificar el manejo de errores del frontend con un interceptor Axios global.
- Agregar al menos pruebas básicas para los servicios críticos (auth, bovinos).
- Crear un componente reutilizable `FormField` para reducir repetición en modales.
