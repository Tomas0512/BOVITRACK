# BOVITRACK — Stack Tecnológico

> Sistema de control y registro de ganado bovino para fincas ganaderas.
> Documento que describe la estructura del proyecto, el tipo de arquitectura elegido y cómo se comunican los componentes con la API.

---

## 1. ¿Qué estructura tiene el proyecto y por qué?

### 1.1 El porqué de la estructura

La estructura de BOVITRACK se eligió siguiendo la que nos enseñaron durante la formación para el desarrollo de proyectos. Es el modelo de referencia que aprendimos para construir aplicaciones web completas: separar el proyecto en capas (cliente, servidor y base de datos), dividir la lógica por responsabilidades dentro de cada capa, y centralizar la comunicación bajo un mismo contrato (la API REST).


### 1.2 Stack Tecnológico

| Capa | Tecnología | Rol |
|---|---|---|
| **Frontend Web** | React 18 + Vite + TypeScript + TailwindCSS 4 | Interfaz de usuario (cliente) |
| **App Móvil** | React Native + Expo SDK 54 | Interfaz de usuario en celulares (cliente) |
| **Backend** | FastAPI + Python 3.12 + SQLAlchemy 2.0 + Alembic | API REST (servidor) |
| **Base de datos** | PostgreSQL 17 (Docker) | Almacenamiento persistente |
| **Infraestructura** | Docker Compose (db, be, fe, mailpit) + nginx | Despliegue y proxy |
| **Pruebas** | pytest (BE) · Vitest + Testing Library (FE) | Calidad |
| **Linting/Formato** | Ruff (BE) · ESLint + Prettier (FE) | Estilo de código |

### 1.3 Tipos de estructura y por qué los usamos

| Ámbito | Tipo de estructura | Por qué la hacemos así |
|---|---|---|
| **Global** | **Modelo Cliente-Servidor** | Existen tres clientes (Web, Móvil y Postman) que consumen un único servidor (FastAPI) que a su vez consulta la base de datos. Es el modelo estándar para aplicaciones web y fue el que aprendimos en la formación: el cliente pide, el servidor responde, nunca el cliente toca la BD directamente. |
| **Backend** | **API REST** | La comunicación entre clientes y servidor se hace con peticiones HTTP sobre recursos (fincas, bovinos, tratamientos…), devolviendo **JSON**. REST es un estilo arquitectónico ampliamente usado porque es simple, sin estado y funciona con el protocolo HTTP que ya conocemos. |
| **Backend (interna)** | **Arquitectura en capas / MVC** | Dentro del servidor separamos: **Model** (modelos ORM SQLAlchemy en `models/`), **Vista** (contratos Pydantic en `schemas/`, que definen cómo se ve la información al salir/entrar) y **Controlador** (rutas HTTP en `routers/` + lógica de negocio en `services/`). Lo hacemos así para que la lógica sea reutilizable, testeable y el código quede ordenado. |
| **Frontend** | **Organización por dominio + inspiración Atomic Design** | Los componentes se agrupan **por módulo de negocio** (`components/bovines/`, `components/food/`…), con carpetas de estructura (`layout/`) y de átomos reutilizables (`ui/`). Seguimos la idea de construir la interfaz de lo simple a lo complejo: átomos → componentes de un módulo → páginas. Así los componentes son fáciles de encontrar y escalan cuando el proyecto crece. |
| **Base de datos** | **Esquema versionado con migraciones (Alembic)** | Las tablas no se crean "a mano" sino mediante **16 migraciones versionadas**. Esto garantiza que todos los desarrolladores tengan la misma estructura de BD y que los cambios sean controlados y reversibles. |
| **App móvil** | **En capas** | `screens/` (interfaz), `services/` (comunicación con la API), `store/` (estado) y `navigation/` (flujo de pantallas). Mismo principio de separación de responsabilidades aplicado a React Native. |

---

## 2. Estructura del proyecto

### 2.1 Estructura completa

```
BOVITRACK/
├── .env.example              # Plantilla de variables de entorno (los secretos no se suben)
├── .gitignore
├── .python-version
├── docker-compose.yml        # Orquesta los servicios: mailpit, db, be, fe
├── README.md                 # Documentación de uso del proyecto
├── be/                       # Backend — FastAPI (Python 3.12)
├── db/                       # Base de datos — PostgreSQL 17 (Docker)
├── docs/                     # Documentación: HUs, RF, RNF, SPRINTS, entrevistas, Postman
├── fe/                       # Frontend — React + Vite + TypeScript
└── mobile/                   # App móvil — React Native + Expo
```

### 2.2 Estructura del backend (`be/`)

```
be/
├── app/
│   ├── main.py               # Punto de entrada: CORS, security headers, rate limit, 22 routers
│   ├── config.py             # Configuración (Pydantic Settings): BD, JWT, SMTP
│   ├── database.py           # Engine SQLAlchemy 2.0 + SessionLocal + Base
│   ├── dependencies.py       # get_db(), get_current_user()
│   ├── permissions.py        # require_permission(módulo, acción) — RBAC
│   ├── models/               # (22 archivos / 33 clases) Modelos ORM SQLAlchemy 2.0
│   │   ├── user.py  role.py  farm.py  farm_invitation.py
│   │   ├── bovine.py  weight.py  movement.py  calf.py
│   │   ├── milk_production.py  treatment.py  sanitary_plan.py
│   │   ├── food.py  economics.py  task.py  paddock.py
│   │   ├── document.py  audit_log.py  department.py …
│   ├── schemas/              # (20) Schemas Pydantic — contrato de entrada/salida (JSON)
│   ├── routers/              # (21 archivos / 22 registrados) Endpoints HTTP por módulo
│   │   ├── auth.py  users.py  farms.py  admin.py
│   │   ├── bovines.py  calves.py  weights.py  movements.py
│   │   ├── treatments.py  sanitary_plan.py  reproductive_events.py
│   │   ├── milk_production.py  food.py  tasks.py
│   │   ├── paddocks.py  land_plots.py  economics.py  documents.py
│   │   ├── employees.py  reports.py  alerts.py
│   ├── services/             # (21) Lógica de negocio — uno por router
│   ├── utils/                # security.py (JWT/bcrypt), email.py, limiter.py, audit_log.py
│   └── tests/                # Pruebas de la aplicación (pendiente de completar)
├── alembic/                  # 16 migraciones de base de datos versionadas
│   └── versions/
├── tests/                    # Pruebas con pytest
├── storage/documents/        # Archivos subidos por los usuarios
├── seed_roles.py             # Scripts de datos semilla (roles, departamentos, demo)
├── seed_departments.py
├── seed_purposes.py
├── seed_test_data.py
├── requirements.txt / pyproject.toml
├── entrypoint.sh             # Ejecuta migraciones y lanza uvicorn
└── Dockerfile
```

### 2.3 Estructura del frontend (`fe/src/`)

```
fe/
├── src/
│   ├── main.tsx              # Punto de entrada
│   ├── App.tsx               # Router y providers
│   ├── index.css             # Tema (TailwindCSS 4, modo claro/oscuro)
│   ├── api/                  # (19 módulos + axios.ts) Clientes HTTP por dominio
│   │   ├── axios.ts          # Instancia central: baseURL, Bearer token, errores
│   │   ├── auth.ts  farms.ts  bovines.ts  calves.ts  food.ts
│   │   ├── treatments.ts  sanitary_plans.ts  reproductive_events.ts
│   │   ├── milk_production.ts  weights.ts  movements.ts  paddocks.ts
│   │   ├── land_plots.ts  economics.ts  reports.ts  documents.ts
│   │   ├── employees.ts  alerts.ts  audit_logs.ts
│   ├── components/           # Componentes agrupados por módulo de negocio
│   │   ├── layout/           # Estructura: Header, Footer, AppLayout, AlertBanner, Breadcrumbs
│   │   ├── ui/               # Átomos reutilizables
│   │   ├── bovines/          # BovineList, BovineFormModal, WeightChart…
│   │   ├── calves/  food/  land_plots/  paddocks/  movements/
│   │   ├── documents/  employees/  audit/
│   ├── context/              # AuthContext (sesión) + ThemeContext (tema)
│   ├── hooks/                # useAuth.ts
│   ├── pages/                # (15) Vistas enrutadas
│   │   ├── LoginPage  RegisterPage  DashboardPage  FarmDetailPage
│   │   ├── BovineDetailPage  EconomicDashboard  ReportsPage …
│   ├── types/                # Tipos TypeScript compartidos
│   └── __tests__/            # Pruebas (Vitest + Testing Library)
├── nginx.conf                # SPA + proxy /api → backend (be:8000)
├── index.html  public/       # Estáticos (logo)
├── package.json  vite.config.ts  tsconfig.json
└── Dockerfile
```

### 2.4 Estructura de la base de datos (`db/`)

```
db/
├── Dockerfile      # Imagen postgres:17 + habilita la extensión uuid-ossp
├── init.sql        # Bootstrap: CREATE EXTENSION IF NOT EXISTS "uuid-ossp"
└── .dockerignore
```

> La base de datos es una pieza deliberadamente mínima. El esquema real
> (más de 30 tablas) no se define aquí sino en las 16 migraciones Alembic del backend.

### 2.5 Estructura de la app móvil (`mobile/src/`)

```
mobile/
└── src/
    ├── navigation/           # RootNavigator (auth vs app) → AuthNavigator / AppNavigator
    ├── screens/              # Pantallas
    │   ├── HomeScreen  DashboardScreen  FarmDetailScreen
    │   └── auth/             # Login, Register, ForgotPassword, ResetPassword
    ├── services/             # api.ts (axios), auth.ts, farms.ts
    ├── store/                # authStore.ts (Zustand)
    ├── theme/                # ThemeContext.tsx + colors.ts (claro/oscuro)
    └── types/                # Tipos TypeScript
```

---

## 3. Comunicación con la API

### 3.1 ¿Cómo se comunican los componentes?

BOVITRACK usa el modelo **REST**: los clientes (Web, Móvil) hacen peticiones HTTP al backend FastAPI, y este responde en **JSON**. El flujo completo de una petición es:

```
Interfaz (React / Móvil)
   │  1. axios inyecta: Authorization: Bearer <access_token>
   ▼
GET /api/v1/farms/{farm_id}/bovines        ← petición REST
   │
   ▼
FastAPI → get_current_user (valida el JWT)
   │
   ├── require_permission("bovinos", "can_read")   ← RBAC por finca
   ▼
Router (valida la petición con un schema Pydantic)
   │
   ▼
Service (lógica de negocio)
   │
   ▼
Modelo SQLAlchemy → PostgreSQL
   │
   ▼
Respuesta JSON (schema Pydantic) → Cliente → Interfaz
```

**Ejemplo real (registro de un bovino):**

1. El usuario llena el formulario en la web.
2. `fe/src/api/bovines.ts` llama a la API con `POST /api/v1/farms/{farm_id}/bovines`.
3. FastAPI valida el JWT, verifica que el usuario pertenece a la finca y tiene permiso de creación.
4. El router valida los datos con `BovineCreate` (Pydantic).
5. El service guarda el registro en PostgreSQL vía el modelo ORM `Bovine`.
6. La API responde `201 Created` con el bovino creado en JSON.
7. La interfaz muestra el bovino en la lista.

### 3.2 Convención de rutas

Todas las rutas parten de `/api/v1`. El diseño es **multi-tenant por finca**: casi todos los recursos cuelgan de `/api/v1/farms/{farm_id}/…` porque ese `farm_id` alimenta el control de acceso (`require_permission` valida la pertenencia a la finca antes de ejecutar el endpoint).

```
/api/v1
├── /auth/*                → público (registro, login, contraseña)
├── /users/me              → usuario autenticado
├── /admin/*               → solicitudes de reactivación
├── /reports/*             → reportes globales
├── /farms
│   ├── /departments  /purposes    → catálogos
│   └── /{farm_id}
│       ├── /bovines  /calves  /weights
│       ├── /treatments  /sanitary-plans  /reproductive-events
│       ├── /milk-production  /food  /paddocks  /land-plots
│       ├── /tasks  /movements  /documents  /employees
│       ├── /economics  /alerts  /audit-logs
│       └── /reports  /statistics  /milk-daily
```

### 3.3 Mapa de rutas por módulo (resumen)

Cada router del backend se corresponde con un módulo de negocio. Los verbos usados son **GET**, **POST**, **PUT** y **DELETE** (no se usa PATCH).

**Autenticación — `/api/v1/auth`**

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/register` | Registro de usuario (envía verificación por email) |
| POST | `/login` | Inicio de sesión (devuelve access + refresh) |
| POST | `/refresh` | Renovar tokens |
| POST | `/forgot-password` | Solicitar restablecimiento de contraseña |
| POST | `/reset-password` | Restablecer contraseña con token |
| POST | `/verify-email` | Verificar correo electrónico |
| GET | `/invitation/{token}` | Información de una invitación a finca |
| POST | `/register-invited` | Registro de un empleado invitado |
| POST | `/logout-all` | Cerrar sesión en todos los dispositivos |
| POST | `/request-reactivation` | Solicitar reactivación de cuenta |

**Usuarios — `/api/v1/users`**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/me` | Datos del usuario autenticado |
| PUT | `/me` | Actualizar perfil |
| DELETE | `/me` | Eliminar cuenta (soft delete) |
| GET | `/farms/{farm_id}/audit-logs` | Registro de auditoría de la finca |

**Fincas — `/api/v1/farms`**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/departments` · `/departments/{id}/cities` · `/purposes` | Catálogos |
| POST | `` · `/bulk` | Crear finca (individual o masiva) |
| GET | `` | Listar fincas del usuario (owner o empleado) |
| GET · PUT · DELETE | `/{farm_id}` | Consultar, actualizar y eliminar una finca |

**Bovinos — `/api/v1/farms/{farm_id}/bovines`**

| Método | Ruta | Propósito |
|---|---|---|
| POST | `` | Registrar un bovino |
| GET | `` · `/{bovine_id}` | Listar y consultar bovinos |
| PUT | `/{bovine_id}` | Actualizar bovino |
| DELETE | `/{bovine_id}` | Eliminar bovino (soft delete) |
| POST · GET | `/{bovine_id}/weights` | Registrar y consultar pesos |

**Terneros — `/api/v1/farms/{farm_id}/calves`**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `` · `/summary` · `/{bovine_id}` | Listado, resumen y detalle de terneros |
| GET · POST | `/{bovine_id}/weights` | Historial y registro de pesos |
| POST | `/{bovine_id}/feeding-plan` | Plan de alimentación |

**Sanidad — tratamientos y plan sanitario**

| Método | Ruta | Propósito |
|---|---|---|
| POST · GET | `/farms/{farm_id}/treatments` | Registrar y listar tratamientos |
| GET · DELETE | `/treatments/{treatment_id}` | Consultar y eliminar tratamiento |
| POST · GET | `/farms/{farm_id}/sanitary-plans` | Crear y listar planes sanitarios |
| PUT · DELETE | `/sanitary-plans/{plan_id}` | Actualizar y eliminar plan |
| POST | `/sanitary-plans/{plan_id}/apply` | Aplicar plan sanitario |

**Reproducción — `/api/v1/farms/{farm_id}/reproductive-events`**

| Método | Ruta | Propósito |
|---|---|---|
| POST · GET · PUT · DELETE | `` / `/{event_id}` | CRUD de eventos reproductivos (servicios, partos, diagnósticos) |

**Producción — `/api/v1/farms/{farm_id}/milk-production`**

| Método | Ruta | Propósito |
|---|---|---|
| POST · GET | `` | Registrar y listar producción de leche |
| GET · DELETE | `/{record_id}` | Consultar y eliminar registro |

**Inventario / Alimentación — `/api/v1/farms/{farm_id}/food`**

| Método | Ruta | Propósito |
|---|---|---|
| POST · GET | `` | Registrar y listar alimentos |
| GET · PUT · DELETE | `/{food_id}` | Consultar, actualizar y eliminar alimento |
| POST · GET | `/consumptions` | Registrar y listar consumos |
| POST | `/purchases` | Registrar compras |
| POST | `/adjust-stock` | Ajustar stock |
| GET | `/movements` · `/low-stock` | Movimientos y alertas de stock bajo |

**Territorio y operación**

| Método | Ruta | Propósito |
|---|---|---|
| CRUD | `/farms/{farm_id}/paddocks` | Potreros |
| CRUD | `/farms/{farm_id}/land-plots` | Lotes |
| CRUD | `/farms/{farm_id}/tasks` | Tareas |
| CRUD | `/farms/{farm_id}/movements` | Movimientos de animales |
| CRUD | `/farms/{farm_id}/economics` | Registros económicos (ingresos/egresos) |
| GET | `/economics/indicators` | Indicadores de rentabilidad |

**Empleados — `/api/v1/farms/{farm_id}`**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/roles` | Roles disponibles |
| POST | `/employees/invite` | Invitar empleado a la finca |
| GET | `/employees` | Listar empleados |
| PUT · DELETE | `/employees/{user_id}` | Actualizar y quitar empleado |

**Documentos — `/api/v1/farms/{farm_id}/documents`**

| Método | Ruta | Propósito |
|---|---|---|
| POST | `` | Subir documento (multipart/form-data) |
| GET | `` | Listar documentos (paginado) |
| GET | `/{document_id}/download` | Descargar documento |
| DELETE | `/{document_id}` | Eliminar documento |

**Reportes — `/api/v1`**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/farms/{farm_id}/statistics` | Estadísticas de la finca |
| GET | `/farms/{farm_id}/milk-daily` | Producción de leche diaria |
| GET | `/farms/{farm_id}/reports` | Reporte de la finca (JSON, PDF o Excel) |
| GET | `/reports/farm-summary` · `/low-stock-alerts` · `/pending-tasks` | Resúmenes globales |

**Alertas y administración**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/farms/{farm_id}/alerts` | Alertas de la finca |
| GET | `/admin/reactivation-requests` | Listar solicitudes de reactivación |
| POST | `/admin/reactivation-requests/{id}/approve` · `/reject` | Aprobar o rechazar solicitudes |

**Health check**

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/` | Estado del servicio |

### 3.4 Autenticación y autorización

- **JWT de doble token**: al iniciar sesión se reciben un **access token** (15 min) y un **refresh token** (7 días). El access viaja en cada petición como `Authorization: Bearer <token>`.
- **RBAC por finca**: cada usuario tiene un rol (Administrador, Capataz, Veterinario, Empleado) dentro de cada finca. Cada rol concede permisos por módulo (`bovinos`, `alimentos`, `sanitario`, `economica`, etc.) y acción (`can_create`, `can_read`, `can_update`, `can_delete`).
- **Protección de rutas**: los endpoints se protegen de forma declarativa en la firma de la ruta con `require_permission("módulo", "acción")`.

---
