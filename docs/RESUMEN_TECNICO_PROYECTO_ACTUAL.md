# Resumen Técnico del Proyecto BoviTrack

**Fecha:** 17 de junio de 2026

---

## 1. ¿Qué es BoviTrack hoy?

BoviTrack es una aplicación full stack para la gestión ganadera que cubre administración de fincas, bovinos, alimentación, sanidad, reproducción, producción de leche, economía, documentos, empleados, tareas, potreros y lotes de tierra.

**Stack tecnológico:**
- **Backend:** FastAPI (Python) con SQLAlchemy + Alembic + PostgreSQL (hot reload vía volúmenes)
- **Frontend web:** React + Vite + TailwindCSS 4 + Nginx
- **App móvil:** React Native + Expo
- **Orquestación:** Docker Compose con healthchecks + volúmenes para desarrollo
- **Correo:** envío real vía SMTP (Gmail) con App Password; alternativas Resend API o log en consola

**Cobertura actual:** 16 Historias de Usuario (HU001–HU016) distribuidas en 8 Sprints, con ~121 endpoints de la API, 15+ páginas web, 4 pantallas móviles, 30 tablas en base de datos (23 modelos ORM), RBAC completo con 4 roles y 32 permisos, autenticación JWT con access/refresh tokens, validación de fechas y rango en reportes, y **carga masiva de bovinos por CSV**.

---

## 2. Arquitectura

El sistema se despliega con **Docker Compose** en 3 servicios:

| Servicio | Puerto | Rol |
|---|---|---|
| `db` | 5432 (solo localhost) | PostgreSQL 17 con volumen persistente |
| `be` | 8000 | FastAPI en contenedor no-root (con hot reload por volumen) |
| `fe` | 5173 → 80 | Nginx sirviendo React SPA + proxy reverso a `/api` |

**Redes segmentadas:**
- `backend_net`: db ↔ be
- `frontend_net`: fe ↔ be

**Healthchecks:** db usa `pg_isready`, be tiene endpoint `/health`.

Archivo: [`docker-compose.yml`](../docker-compose.yml)

---

## 3. Frontend — Todo lo implementado

### 3.1 Páginas (15+)

| Ruta | Archivo |
|---|---|
| `/login` | [`LoginPage.tsx`](../fe/src/pages/LoginPage.tsx) |
| `/register` | [`RegisterPage.tsx`](../fe/src/pages/RegisterPage.tsx) |
| `/register?invited=1` | [`InvitedRegisterPage.tsx`](../fe/src/pages/InvitedRegisterPage.tsx) |
| `/forgot-password` | [`ForgotPasswordPage.tsx`](../fe/src/pages/ForgotPasswordPage.tsx) |
| `/reset-password` | [`ResetPasswordPage.tsx`](../fe/src/pages/ResetPasswordPage.tsx) |
| `/dashboard` | [`DashboardPage.tsx`](../fe/src/pages/DashboardPage.tsx) |
| `/farms/:id` | [`FarmDetailPage.tsx`](../fe/src/pages/FarmDetailPage.tsx) |
| `/farms/new` | [`CreateFarmPage.tsx`](../fe/src/pages/CreateFarmPage.tsx) |
| `/economics` | [`EconomicDashboard.tsx`](../fe/src/pages/EconomicDashboard.tsx) |
| `/reports` | [`ReportsPage.tsx`](../fe/src/pages/ReportsPage.tsx) |
| `/bovines/:id` | [`BovineDetailPage.tsx`](../fe/src/pages/BovineDetailPage.tsx) |
| `/terms` | [`TermsPage.tsx`](../fe/src/pages/TermsPage.tsx) |
| `/privacy` | [`PrivacyPage.tsx`](../fe/src/pages/PrivacyPage.tsx) |
| `/reactivation` | [`RequestReactivationPage.tsx`](../fe/src/pages/RequestReactivationPage.tsx) |
| `/` | [`HomePage.tsx`](../fe/src/pages/HomePage.tsx) |

### 3.2 Formularios multi-step con paginación

Se implementaron **9 flujos multi-step** (CreateFarmPage, bovines, movements, food, reports, documents, economics, employees, land_plots) con navegación entre pasos, validación por paso y estado compartido.

### 3.3 API clients

[`fe/src/api/`](../fe/src/api) contiene 20 módulos Axios:

| Archivo | Funcionalidad |
|---|---|
| `auth.ts` | Login, register, refresh, forgot/reset password |
| `farms.ts` | CRUD fincas, listar, detalle |
| `bovines.ts` | CRUD bovinos, historial, filtros |
| `movements.ts` | Movimientos de animales |
| `food.ts` | Alimentación y consumos |
| `reports.ts` | Reportes y estadísticas |
| `documents.ts` | Subida y gestión de documentos |
| `economics.ts` | Registros económicos |
| `employees.ts` | Empleados por finca |
| `land_plots.ts` | Lotes de tierra |
| `paddocks.ts` | Potreros y pastoreo |
| `sanitary_plans.ts` | Planes sanitarios |
| `treatments.ts` | Tratamientos veterinarios |
| `calves.ts` | Gestión de crías/terneros |
| `milk_production.ts` | Producción de leche |
| `reproductive_events.ts` | Eventos reproductivos |
| `weights.ts` | Pesajes y curvas de peso |
| `tasks.ts` | Tareas asignadas |
| `alerts.ts` | Alertas y notificaciones |
| `audit_logs.ts` | Logs de auditoría |

### 3.4 Contextos y tema

- [`ThemeContext.tsx`](../fe/src/context/ThemeContext.tsx) — Dark/light mode con persistencia + `ThemeToggle`
- [`AuthContext.tsx`](../fe/src/context/AuthContext.tsx) — Estado de autenticación global
- [`ProtectedRoute.tsx`](../fe/src/components/ProtectedRoute.tsx) — Guard de rutas autenticadas

### 3.5 Componentes reutilizables

- **FormModal pattern:** Modal genérico reutilizable para formularios CRUD
- Componentes UI modulares en [`fe/src/components/ui/`](../fe/src/components/ui/)
- Componentes específicos por módulo: bovines/, calves/, documents/, employees/, food/, land_plots/, movements/, paddocks/, audit/

### 3.6 Estilo

- **TailwindCSS 4** con configuración personalizada
- Tema claro/oscuro completamente implementado
- Diseño responsivo

### 3.7 Configuración

- [`vite.config.ts`](../fe/vite.config.ts) — Vite + configuración de tests
- [`Dockerfile`](../fe/Dockerfile) — Build multi-stage (compilación React + Nginx)
- [`nginx.conf`](../fe/nginx.conf) — SPA routing + proxy `/api` al backend
- [`package.json`](../fe/package.json) — Dependencias y scripts

---

## 4. Backend — Todo lo implementado

### 4.1 Routers y endpoints

[`be/app/routers/`](../be/app/routers) contiene los routers que exponen **~121 endpoints** de la API REST documentados en `/docs` (Swagger):

| Router | Endpoints clave |
|---|---|
| `auth.py` | register, login, refresh, forgot-password, reset-password, logout, verify-email |
| `users.py` | CRUD usuarios, perfil, cambiar contraseña |
| `farms.py` | CRUD fincas, listar, detalle, estadísticas |
| `bovines.py` | CRUD bovinos, filtrar, historial |
| `movements.py` | Registrar movimientos, historial |
| `food.py` | Alimentación, consumos, stocks |
| `reports.py` | Reportes agregados |
| `documents.py` | Subir, listar, descargar documentos |
| `economics.py` | Registros económicos, balances |
| `employees.py` | CRUD empleados por finca |
| `land_plots.py` | CRUD lotes de tierra |
| `paddocks.py` | CRUD potreros, asignación de bovinos |
| `sanitary_plan.py` | Planes sanitarios, programación |
| `treatments.py` | Tratamientos, historial clínico |
| `calves.py` | Gestión de crías |
| `milk_production.py` | Registro de producción de leche |
| `reproductive_events.py` | Eventos: celo, monta, diagnóstico, parto |
| `weights.py` | Pesajes y curvas de peso |
| `tasks.py` | CRUD tareas, asignación |
| `alerts.py` | Alertas, notificaciones |
| `admin.py` | Panel administrativo |
| `invitations.py` | Invitaciones a fincas |
| `departments.py` | Departamentos y ciudades |

### 4.2 Modelos ORM (20+)

Definidos en [`be/app/models/`](../be/app/models/):

| Modelo | Tabla |
|---|---|
| `User` | `users` |
| `Role` | `role` |
| `Permission` | `permission` |
| `Farm` | `farm` |
| `UserFarm` | `user_farm` |
| `LandPlot` | `land_plot` |
| `Paddock` | `paddock` |
| `PaddockHerd` | `paddock_herd` |
| `Bovine` | `bovine` |
| `BovineIdentification` | `bovine_identification` |
| `BovineAudit` | `bovine_audit` |
| `Movement` | `animal_movement` |
| `Food` | `food` |
| `Consumption` | `consumption` |
| `StockMovement` | `stock_movement` |
| `Weight` | `weight` |
| `SanitaryPlan` | `sanitary_plan` |
| `Treatment` | `treatment` |
| `ReproductiveEvent` | `reproductive_event` |
| `MilkProduction` | `milk_production` |
| `EconomicRecord` | `economic_record` |
| `Document` | `document` |
| `Task` | `task` |
| `AuditLog` | `audit_log` |
| `FarmInvitation` | `farm_invitation` |
| `EmailVerificationToken` | `email_verification_token` |
| `PasswordResetToken` | `password_reset_token` |
| `ReactivationRequest` | `reactivation_request` |
| `Department` | `department` |
| `City` | `city` |
| `Purpose` | `purpose` |

### 4.3 Servicios

[`be/app/services/`](../be/app/services/) contiene **22 servicios** desacoplados por módulo de negocio (auth_service, farm_service, bovine_service, food_service, etc.), cada uno con su lógica de negocio específica.

### 4.4 Seguridad y RBAC

- **4 roles:** Administrador, Propietario, Empleado, Visitante
- **32 permisos** (8 módulos × 4 operaciones CRUD)
- Control de acceso por finca (`UserFarm`)
- JWT con **access token** (corto) + **refresh token** (largo)
- **Token versioning:** permite invalidar sesiones (logout real)
- Protección de **último administrador** (no se puede eliminar ni degradar)
- Contraseñas hasheadas con **bcrypt**
- CORS configurado desde variable `FRONTEND_URL`
- Backend ejecuta como **usuario no-root** en contenedor
- **Invitación de empleados:** usuarios invitados via `UserFarm` pueden listar y acceder a la finca (no solo el `owner_id`)

### 4.5 Email

- **Entrega real:** SMTP (Gmail) vía App Password (`EMAIL_BACKEND=smtp`). Los enlaces de verificación/recuperación son envíos reales.
- **Alternativas:** API Resend configurada como respaldo, o `log` para imprimir el enlace en consola.
- **Fallback:** Log a consola si no hay SMTP ni Resend
- Flujos: bienvenida, verificación de email, recuperación de contraseña, invitación a finca

### 4.6 Migraciones Alembic

[`be/alembic/versions/`](../be/alembic/versions/) contiene **16 migraciones lineales** (sin cabezas múltiples):

1. `eeee1c29cefa` — Tablas users + password_reset_tokens
2. `c9ff44fd3509` — Schema inicial completo
3. `e1f2a3b4c5d6` — Seed roles y permisos
4. `a1b2c3d4e5f6` — Vistas y funciones
5. `c1d2e3f4a5b6` — Seguridad, consentimiento, auditoría
6. `f1a2b3c4d5e6` — Farm invitation
7. `fb563e20cc8e` — Tablas de dominio (departamentos, ciudades)
8. `9d8e7f6a5b4c` — Seed departamentos + cambio farm city
9. `g1h2i3j4k5l6` — Reactivación, ubicación, pastoreo
10. `h1i2j3k4l5m6` — Farm ID en audit log
11. `i1j2k3l4m5n6` — Sanitary plan
12. `j1k2l3m4n5o6` — Reproductive event
13. `k1l2m3n4o5p6` — Economic record
14. `l1m2n3o4p5q6` — Animal movement
15. `m1n2o3p4q5r6` — Document
16. `n1o2p3q4r5s6` — Stock movement

Configuración: [`be/alembic.ini`](../be/alembic.ini), [`be/alembic/env.py`](../be/alembic/env.py)

---

## 5. Base de datos

**Motor:** PostgreSQL 17

**Esquema actual:** 30 tablas normalizadas que cubren:
- Usuarios y autenticación
- Roles y permisos (RBAC)
- Fincas y relación usuario-finca
- Departamentos y ciudades
- Propósitos productivos
- Lotes de tierra y potreros
- Bovinos, identificaciones y auditoría
- Planes sanitarios y tratamientos
- Eventos reproductivos
- Alimentación, consumos y movimientos de stock
- Pesajes
- Producción de leche
- Movimientos de animales
- Registros económicos
- Documentos
- Tareas
- Invitaciones a fincas
- Solicitudes de reactivación
- Logs de auditoría
- Tokens de verificación de email y recuperación de contraseña

**Migraciones:** Lineales con Alembic (sin cabezas múltiples). Cada migración es revisada antes de crear la siguiente.

Archivos de inicialización: [`db/Dockerfile`](../db/Dockerfile), [`db/init.sql`](../db/init.sql)

---

## 6. Seguridad

| Medida | Estado |
|---|---|
| Hashing bcrypt | Implementado |
| JWT access + refresh tokens | Implementado |
| Token versioning (logout real) | Implementado |
| Expiración configurable de tokens | Implementado |
| CORS con origen permitido | Implementado |
| Contenedor no-root (backend) | Implementado |
| Puerto DB no expuesto al host | Implementado |
| Prevención enumeración usuarios | Implementado |
| Token recuperación un solo uso | Implementado |
| RBAC completo (4 roles, 32 permisos) | Implementado |
| Protección último administrador | Implementado |
| Auditoría de acciones críticas | Implementado |
| Rate limiting | Pendiente (HU014, fuera de alcance) |
| HTTPS en producción | Pendiente (despliegue futuro) |

---

## 7. Mobile App (React Native + Expo)

Carpeta: [`mobile/`](../mobile/)

**Pantallas de autenticación:**
- [`LoginScreen.tsx`](../mobile/src/screens/auth/LoginScreen.tsx)
- [`RegisterScreen.tsx`](../mobile/src/screens/auth/RegisterScreen.tsx)
- [`ForgotPasswordScreen.tsx`](../mobile/src/screens/auth/ForgotPasswordScreen.tsx)
- [`ResetPasswordScreen.tsx`](../mobile/src/screens/auth/ResetPasswordScreen.tsx)

**Pantallas internas:**
- [`DashboardScreen.tsx`](../mobile/src/screens/DashboardScreen.tsx)
- [`FarmDetailScreen.tsx`](../mobile/src/screens/FarmDetailScreen.tsx)
- [`HomeScreen.tsx`](../mobile/src/screens/HomeScreen.tsx)

**Características:**
- Navegación con React Navigation (AuthNavigator + AppNavigator + RootNavigator)
- Dark/light mode con ThemeContext
- Validación inline en formularios
- Paleta de colores web: `#59930a`
- Arquitectura modular (screens/, navigation/, theme/)

---

## 8. Infraestructura

### Docker Compose

4 servicios orquestados:

```yaml
services:
  db:         # PostgreSQL 17 + healthcheck + volumen persistente
  be:         # FastAPI, multi-stage build, usuario no-root
  fe:         # React + Nginx, multi-stage build
```

Redes: `backend_net` (db, be) + `frontend_net` (fe, be)
Volumen: `bovitrack_data` (persistencia PostgreSQL)

### Variables de entorno

- [`.env.example`](../.env.example) — Variables raíz del proyecto
- [`be/.env.example`](../be/.env.example) — Variables específicas del backend
- [`fe/.env.example`](../fe/.env.example) — Variables del frontend (VITE_API_URL)

---

## 9. Tablero ClickUp

- **Space:** BOVITRACK
- **8 listas** (una por Sprint: 1 al 7 + **Sprint 8 – Cierre Web**)
- **16 Historias de Usuario** (HU001–HU016) con checklists desglosados por tarea técnica
- Cada HU incluye criterios de aceptación, subtareas y asignación
- Guía paso a paso para armar/terminar el tablero: `CLICKUP_BOARD.md` (en el escritorio)
- HU016 (modo offline): **fuera de alcance** (pospuesta por fecha límite 23/08/2026)

---

## 10. Resumen Ejecutivo

**Estado actual:** El proyecto cubre los Sprints 1 al 8 con las **16 HUs** planificadas. Todas las funcionalidades core de gestión ganadera están implementadas: autenticación, fincas, bovinos, alimentación, sanidad, reproducción, producción de leche, economía, documentos, empleados, tareas, potreros y lotes de tierra, alertas/notificaciones, auditoría y **reportes exportables PDF/Excel**. Funcionan el flujo de invitación de empleados, la **recuperación/verificación de cuenta por correo**, la **validación de fechas en reportes**, la **relación animal↔potrero** y la **carga masiva de bovinos por CSV**. La rama de cierre (`fix/auditoria-seguridad`) integra correcciones de seguridad (control de acceso por finca), validaciones de formularios y mejoras de UI/UX.

**Métrica general:**
- ~121 endpoints de la API en 23 routers (documentados en Swagger `/docs`)
- 15+ páginas web con TailwindCSS 4 y modo oscuro
- 7 pantallas móviles (4 auth + 3 internas)
- 30 tablas en PostgreSQL con migraciones lineales (23 modelos ORM)
- 22 servicios backend desacoplados
- 20 API clients en el frontend
- RBAC con 4 roles y 32 permisos
- Autenticación JWT con token versioning
- 9 formularios multi-step con paginación
- Docker Compose con 4 servicios y healthchecks
- Backend con hot reload vía volúmenes Docker (sin rebuild)
- 16 migraciones Alembic lineales

**Pendiente (fuera de alcance):**
- HU016 — Modo offline (pospuesta por fecha límite 23/08/2026)
- HU014 y HU015 — en curso dentro del **Sprint 8 (Final)** (08–23 agosto 2026): alertas/notificaciones (Tomas) y auditorías (Camilo)

**Documentación relacionada:** [`README.md`](../README.md)
