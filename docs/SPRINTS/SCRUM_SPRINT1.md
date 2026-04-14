# SCRUM — Sprint 1
## BoviTrack · Autenticación, RBAC y Estructura de Fincas (Backend)

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 1 |
| **Duración** | 2 semanas |
| **Fecha inicio** | 9 de marzo de 2026 |
| **Fecha fin** | 22 de marzo de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner) |

---

## Objetivo del Sprint

> Construir el núcleo de autenticación del sistema con JWT, RBAC completo (4 roles, 32 permisos), gestión de empleados y auditoría de accesos. Además, establecer la base de datos de fincas con departamentos DANE y los modelos backend de lotes. Al final del sprint el sistema debe tener autenticación funcional y los endpoints de fincas operativos.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU001 | Como Administrador quiero generar usuarios, roles y accesos para controlar quién puede entrar al sistema | Alta | 8 |
| HU002 (parcial) | Como Administrador quiero registrar fincas y lotes para organizar la estructura productiva — **tareas backend: modelos, migraciones y CRUD de fincas** | Alta | 3 |

**Total Story Points del Sprint: 11**

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

### HU002 (parcial) — Fincas: Modelos y CRUD Backend

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 2.1 | Modelo ORM `Farm` con campos (nombre, área, departamento, teléfono) | Camilo | ✅ Hecho | 2h |
| 2.2 | Migración Alembic con seed de 33 departamentos de Colombia (códigos DANE) | Camilo | ✅ Hecho | 3h |
| 2.3 | CRUD completo de fincas (`GET /farms`, `POST`, `PUT`, `DELETE`) | Camilo | ✅ Hecho | 4h |
| 2.4 | Modelo ORM `LandPlot` con validación de nombre único por finca | Tomas | ✅ Hecho | 2h |

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

**Fecha:** 22 de marzo de 2026  
**Participantes:** Camilo Ortiz, Tomas Cañon

### Incremento entregado

| Módulo | Entregado | Observaciones |
|---|---|---|
| Autenticación completa | ✅ | Register, Login, ForgotPassword, ResetPassword |
| RBAC (4 roles, 32 permisos) | ✅ | Administrador, Capataz, Veterinario, Empleado |
| Módulo de empleados | ✅ | Asignar/modificar/retirar roles en finca |
| Historial de auditoría | ✅ | Componente colapsable en detalle de finca |
| Modelo y CRUD de fincas | ✅ | CRUD + departamentos Colombia (DANE) |
| Modelo de lotes | ✅ | ORM LandPlot con nombre único por finca |

### Story Points completados: 11 / 11 ✅

### Demo realizado:

1. Registro de usuario → auto-login → dashboard
2. Autenticación JWT con access y refresh token
3. Sistema RBAC con 4 roles y 32 permisos
4. Asignación de rol a empleado en la finca
5. Historial de auditoría de accesos
6. CRUD backend de fincas con departamentos DANE

---

## Sprint Retrospectiva

### ¿Qué salió bien?

- La arquitectura modular (router → service → model) se estableció desde el inicio y facilitará los módulos siguientes.
- El sistema RBAC centralizado con `require_permission` simplificó la protección de todos los endpoints.
- Las migraciones Alembic secuenciales mantuvieron la base de datos versionada y reproducible.

### ¿Qué se puede mejorar?

- Faltan pruebas unitarias para los servicios del backend.
- Los mensajes de error del backend no siempre llegan al frontend de forma legible.

### Acciones para el Sprint 2

- Completar el frontend de fincas y lotes usando los endpoints ya disponibles.
- Aplicar patrones de componentes frontend reutilizables desde el inicio.
