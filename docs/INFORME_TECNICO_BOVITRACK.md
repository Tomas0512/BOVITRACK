# Informe Técnico — BoviTrack

**Proyecto:** BoviTrack — Sistema de Control y Registro de Ganado Bovino  
**Equipo:** Camilo Ortiz (Product Owner) · Tomas Cañon (Scrum Master)  
**Fecha:** 26 de marzo de 2026  

---

## Tabla de Contenidos

1. [¿Qué es BoviTrack?](#1-qué-es-bovitrack)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Cómo levantar el proyecto](#3-cómo-levantar-el-proyecto)
4. [Explicación de cada archivo](#4-explicación-de-cada-archivo)
5. [Cómo funciona cada punto de la lista de chequeo](#5-cómo-funciona-cada-punto-de-la-lista-de-chequeo)
6. [Cómo probar con Swagger (OpenAPI)](#6-cómo-probar-con-swagger-openapi)
7. [Cómo probar con Postman](#7-cómo-probar-con-postman)
8. [Cómo probar desde el navegador (Frontend)](#8-cómo-probar-desde-el-navegador-frontend)
9. [Glosario técnico](#9-glosario-técnico)

---

## 1. ¿Qué es BoviTrack?

BoviTrack es una aplicación web para gestionar fincas ganaderas. Permite:

- **Registrarse e iniciar sesión** de forma segura (JWT, bcrypt)
- **Crear y administrar fincas** con datos reales (departamentos de Colombia)
- **Registrar bovinos** con genealogía (padre/madre), identificaciones múltiples
- **Controlar producción de leche** (ordeño manual/mecánico por bovino)
- **Gestionar sanidad** (tratamientos con producto, dosis, vía de administración)
- **Inventario de alimentos** con control de stock y consumos
- **Tareas operativas** con prioridad, fecha límite y asignación a trabajadores
- **Potreros** con capacidad máxima y estados (libre/ocupado/en descanso)
- **Reportes** con vistas SQL (producción diaria, alertas de stock bajo, tareas pendientes)
- **Roles y permisos** (Administrador, Capataz, Veterinario, Empleado) por finca

---

## 2. Arquitectura del Proyecto

### Diagrama general

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose                         │
│                                                           │
│  ┌──────────┐      ┌──────────────┐      ┌────────────┐ │
│  │    fe     │      │      be      │      │     db     │ │
│  │  (nginx)  │─────▶│   (FastAPI)  │─────▶│ (Postgres) │ │
│  │ puerto 80 │ /api │  puerto 8000 │      │ puerto 5432│ │
│  └──────────┘      └──────────────┘      └────────────┘ │
│   frontend_net      backend_net + frontend_net  backend_net│
└──────────────────────────────────────────────────────────┘
         │
    Puerto 5173 (host)
         │
    Tu navegador
```

### ¿Qué hace cada servicio?

| Servicio | Tecnología | ¿Qué hace? |
|----------|------------|-------------|
| **fe** | React + TypeScript + Vite + nginx | Es la interfaz visual. Lo que ves en el navegador. nginx sirve los archivos estáticos y reenvía las peticiones `/api/` al backend. |
| **be** | Python + FastAPI + SQLAlchemy | Es el cerebro. Recibe peticiones HTTP, valida datos, ejecuta lógica de negocio y habla con la base de datos. |
| **db** | PostgreSQL 17 | Es la memoria permanente. Guarda todos los datos: usuarios, fincas, bovinos, roles, etc. |

### ¿Cómo se comunican?

1. Tú abres `http://localhost:5173` en el navegador
2. nginx te sirve la app React (HTML/JS/CSS)
3. Cuando la app necesita datos (ej: listar fincas), hace una petición a `/api/v1/farms/`
4. nginx reenvía esa petición al backend (FastAPI en puerto 8000)
5. FastAPI valida el token JWT, verifica permisos RBAC, consulta PostgreSQL
6. PostgreSQL retorna los datos
7. FastAPI responde en JSON
8. React muestra los datos en pantalla

---

## 3. Cómo levantar el proyecto

### Requisitos previos

- Docker Desktop instalado y corriendo
- Git (para clonar el repositorio)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Tomas0512/BOVITRACK.git
cd BOVITRACK

# 2. Crear archivo .env (copiar del ejemplo)
cp .env.example .env

# 3. Levantar los 3 servicios
docker compose up -d

# 4. Aplicar las migraciones de base de datos
docker exec bovitrack_be alembic upgrade head

# 5. ¡Listo! Abrir en el navegador:
#    - Frontend: http://localhost:5173
#    - Swagger:  http://localhost:5173/docs (vía proxy)
#    - Swagger directo: http://localhost:8000/docs
```

### Comandos útiles

| Comando | ¿Qué hace? |
|---------|-------------|
| `docker compose up -d` | Levanta todo en segundo plano |
| `docker compose stop` | Pausa los contenedores (sin borrarlos) |
| `docker compose down` | Detiene y **elimina** los contenedores |
| `docker compose logs be -f` | Ver logs del backend en tiempo real |
| `docker compose logs fe -f` | Ver logs del frontend en tiempo real |
| `docker exec bovitrack_be alembic upgrade head` | Aplicar migraciones pendientes |
| `docker exec bovitrack_be alembic history` | Ver historial de migraciones |

### Desarrollo local del frontend (sin Docker)

Si quieres ver cambios en tiempo real mientras editas el código React:

```bash
cd fe
pnpm install    # Instalar dependencias (solo la primera vez)
pnpm dev        # Servidor de desarrollo en http://localhost:5173
```

> **Nota:** El backend y la base de datos deben estar corriendo en Docker.

---

## 4. Explicación de cada archivo

### 4.1. Raíz del proyecto

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `docker-compose.yml` | Define los 3 servicios (fe, be, db), sus redes y dependencias. Es como el "plano" que le dice a Docker qué contenedores crear y cómo conectarlos. Las credenciales vienen del archivo `.env`. |
| `.env.example` | Plantilla de variables de entorno. Se copia como `.env` y contiene: credenciales de BD, clave secreta JWT, URLs del frontend, configuración de correo SMTP. |
| `README.md` | Documentación general del proyecto: stack tecnológico, módulos, instrucciones de instalación. |

### 4.2. Base de Datos (`db/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `db/Dockerfile` | Crea la imagen de PostgreSQL 17. Copia `init.sql` para ejecutarlo automáticamente la primera vez que se crea la base de datos. |
| `db/init.sql` | Habilita la extensión `uuid-ossp` que permite generar identificadores UUID. Las tablas NO se crean aquí sino con Alembic. |

### 4.3. Backend (`be/`)

#### Configuración e infraestructura

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `be/Dockerfile` | Construye la imagen del backend en dos etapas: primero instala dependencias, luego copia el código. Corre como usuario `appuser` (no como root) por seguridad. |
| `be/requirements.txt` | Lista de paquetes Python que necesita el backend. Son 17 dependencias principales: FastAPI, SQLAlchemy, Alembic, bcrypt, JWT, slowapi, etc. |
| `be/alembic.ini` | Configuración de Alembic (la herramienta de migraciones de base de datos). |
| `be/alembic/env.py` | Conecta Alembic con los modelos SQLAlchemy para que pueda generar y aplicar migraciones automáticamente. |

#### Núcleo de la aplicación (`be/app/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `be/app/config.py` | Carga y valida TODAS las variables de entorno usando Pydantic Settings. Si falta alguna variable crítica (como SECRET_KEY), la aplicación no arranca. Exporta un objeto `settings` que se usa en todo el backend. |
| `be/app/database.py` | Crea la conexión a PostgreSQL con SQLAlchemy. Exporta `SessionLocal` (fábrica de sesiones) y `Base` (clase padre de todos los modelos ORM). |
| `be/app/main.py` | **Punto de entrada principal del backend.** Crea la app FastAPI, configura: CORS (qué dominios pueden hacer peticiones), security headers (protección contra XSS/clickjacking), rate limiter (límite de peticiones por IP), y registra los 10 routers de endpoints. |
| `be/app/dependencies.py` | Funciones que se inyectan en los endpoints usando `Depends()`. `get_db()` provee una sesión de BD. `get_current_user()` valida el token JWT y retorna el usuario autenticado. |
| `be/app/permissions.py` | Sistema RBAC. La función `require_permission(modulo, accion)` verifica que el usuario tenga el permiso necesario para acceder al recurso dentro de una finca específica. |

#### Modelos ORM (`be/app/models/`)

Los modelos definen las tablas de la base de datos usando clases Python. SQLAlchemy traduce estas clases a tablas SQL automáticamente.

| Archivo | ¿Qué tablas define? | ¿Para qué sirve? |
|---------|---------------------|-------------------|
| `models/__init__.py` | — | Re-exporta todos los modelos para que Alembic los detecte al generar migraciones. |
| `models/user.py` | `users`, `password_reset_tokens` | Define la tabla de usuarios (nombre, email, contraseña hasheada, consentimientos legales) y la de tokens de recuperación de contraseña. |
| `models/farm.py` | `farm`, `user_farm`, `role`, `permission`, `department`, `city`, `purpose`, `land_plot` | Define fincas, la relación usuario↔finca↔rol (RBAC), catálogos de departamentos/ciudades/propósitos, y lotes de terreno. |
| `models/bovine.py` | `bovine`, `bovine_identification`, `bovine_audit`, `paddock`, `paddock_herd`, `food`, `consumption`, `treatment`, `milk_production`, `task` | Todas las tablas del dominio ganadero: bovinos con genealogía, potreros, alimentos con stock, tratamientos sanitarios, producción de leche y tareas. |
| `models/audit_log.py` | `audit_log` | Tabla de auditoría genérica: registra qué usuario hizo qué acción sobre qué entidad, con detalles en JSON y marca de tiempo. |
| `models/email_verification_token.py` | `email_verification_tokens` | Tokens de verificación de correo electrónico post-registro. |

#### Routers / Endpoints (`be/app/routers/`)

Cada router agrupa los endpoints de un módulo funcional.

| Archivo | Prefijo URL | Endpoints | ¿Para qué sirve? |
|---------|-------------|-----------|-------------------|
| `routers/auth.py` | `/api/v1/auth` | `POST /register`, `POST /login`, `POST /refresh`, `POST /forgot-password`, `POST /reset-password`, `POST /verify-email`, `POST /logout-all` | Todo el flujo de autenticación: registro, login, refresh de tokens, recuperación de contraseña, verificación de email, cierre de todas las sesiones. Tiene rate limiting: registro 5/min, login 10/min, forgot-password 3/min. |
| `routers/users.py` | `/api/v1/users` | `GET /me`, `DELETE /me` | Obtener perfil del usuario actual (incluye rol), eliminar cuenta propia (requiere escribir "ELIMINAR" como confirmación). |
| `routers/farms.py` | `/api/v1/farms` | `GET /departments`, `GET /purposes`, `POST /`, `POST /bulk`, `GET /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` | CRUD completo de fincas. Al crear una finca, se asigna automáticamente el rol "Administrador" al creador. Soporta creación masiva. |
| `routers/bovines.py` | `/api/v1/farms/{farm_id}/bovines` | CRUD completo con filtros (sexo, estado, propósito) | Gestión de bovinos dentro de una finca. Soft delete (marca como "retirado"). Protegido por RBAC módulo `bovinos`. |
| `routers/treatments.py` | `/api/v1/farms/{farm_id}/treatments` | Create, List, Get, Delete | Tratamientos sanitarios: tipo, producto, dosis, vía de administración, diagnóstico. Protegido por RBAC módulo `tratamientos`. |
| `routers/milk_production.py` | `/api/v1/farms/{farm_id}/milk-production` | Create, List, Get, Delete | Registros de ordeño: litros, tipo (manual/mecánico), fecha, bovino. Protegido por RBAC módulo `produccion_leche`. |
| `routers/food.py` | `/api/v1/farms/{farm_id}/food` | CRUD alimentos + Create/List consumos | Inventario de alimentos con stock, precio, proveedor, vencimiento. Los consumos descuentan automáticamente el stock (valida que haya suficiente). Protegido por RBAC módulo `alimentos`. |
| `routers/tasks.py` | `/api/v1/farms/{farm_id}/tasks` | CRUD completo con filtros (estado, prioridad, asignado a) | Tareas operativas con fecha límite y prioridad. Protegido por RBAC módulo `tareas`. |
| `routers/paddocks.py` | `/api/v1/farms/{farm_id}/paddocks` | CRUD completo | Potreros con capacidad máxima y estados. Protegido por RBAC módulo `potreros`. |
| `routers/reports.py` | `/api/v1` | 5 endpoints de reportes | Estadísticas de finca (función SQL), producción lechera diaria (vista SQL), resumen de fincas, alertas de stock bajo, tareas pendientes. |

#### Schemas Pydantic (`be/app/schemas/`)

Los schemas definen la "forma exacta" de los datos que la API acepta (request) y retorna (response). Si los datos no cumplen el schema, FastAPI retorna un error 422 automáticamente.

| Archivo | ¿Qué valida? | Validaciones principales |
|---------|---------------|-------------------------|
| `schemas/user.py` | Usuarios y autenticación | Email válido (EmailStr), contraseña fuerte (8+ chars, mayúscula, minúscula, número, especial), nombres solo letras, documento max 50 chars, consentimientos obligatorios. Tipos de documento: CC, CE, TI, PP, NIT. |
| `schemas/farm.py` | Fincas | Nombre ≥2 chars, dirección ≥5 chars, área >0, unidad de área (hectáreas/m²/fanegadas). |
| `schemas/bovine.py` | Bovinos | Sexo (macho/hembra), tipo de entrada (nacimiento/compra/donación/traspaso), pesos numéricos. |
| `schemas/treatment.py` | Tratamientos | Tipo, producto, dosis, vía de administración, diagnóstico, síntomas. |
| `schemas/milk_production.py` | Producción de leche | Litros >0, tipo de ordeño (manual/mecánico). |
| `schemas/food.py` | Alimentos y consumos | Stock, precio, proveedor, vencimiento. Consumos: cantidad >0, se valida stock suficiente. |
| `schemas/task.py` | Tareas | Asignado a (obligatorio), prioridad, tipo, fecha límite. |
| `schemas/paddock.py` | Potreros | Área >0, capacidad máxima >0, estado, cobertura. |

#### Services — Lógica de negocio (`be/app/services/`)

Los servicios contienen la lógica de negocio separada de los endpoints. Cada servicio se encarga de un módulo.

| Archivo | ¿Qué lógica contiene? |
|---------|----------------------|
| `services/auth_service.py` | **Registro:** verifica email/documento no duplicado, hashea contraseña con bcrypt, guarda consentimientos con timestamp, crea token de verificación de email, registra en auditoría. **Login:** valida contraseña, verifica cuenta activa, genera JWT access (15min) + refresh (7 días). **Forgot/Reset password:** genera token UUID con expiración 1 hora, siempre retorna éxito (previene enumeración de usuarios), valida token al resetear. **Logout-all:** incrementa `token_version` para invalidar TODOS los tokens existentes. |
| `services/farm_service.py` | CRUD de fincas. Al crear, verifica que el identificador no esté duplicado, crea la finca Y automáticamente asigna el rol "Administrador" al creador (vía `UserFarm`). Soporta creación masiva. Soft delete. Registra en auditoría. |
| `services/bovine_service.py` | CRUD de bovinos con filtros opcionales (sexo, estado, propósito). Actualización parcial (solo los campos que envíes). Soft delete cambia estado a "retirado". |
| `services/treatment_service.py` | CRUD de tratamientos sanitarios. Hard delete (sin papelera). Filtro por bovino. |
| `services/milk_production_service.py` | CRUD de registros de producción de leche. Hard delete. Filtro por bovino. |
| `services/food_service.py` | CRUD de alimentos (soft delete) y consumos. **Importante:** al crear un consumo, valida que haya stock suficiente antes de descontar. Si no hay, retorna error 400. |
| `services/task_service.py` | CRUD de tareas operativas con filtros (estado, prioridad, asignado a). Ordenadas por fecha límite ascendente. |
| `services/paddock_service.py` | CRUD de potreros. Soft delete. |
| `services/audit_service.py` | Función `add_audit_log()` que registra acciones en la tabla `audit_log` con: usuario, acción, entidad, ID de entidad y detalles en JSON. |

#### Utils — Utilidades (`be/app/utils/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `utils/security.py` | Funciones de seguridad: `hash_password()` → hashea con bcrypt, `verify_password()` → compara hash, `create_access_token()` → genera JWT con expiración, `create_refresh_token()`, `decode_token()` → decodifica y valida JWT. |
| `utils/email.py` | Envío de correos electrónicos. En desarrollo imprime el enlace en la consola del backend. En producción se descomentan las funciones SMTP reales. Dos funciones: `send_password_reset_email()` y `send_email_verification()`. |
| `utils/audit_log.py` | Logger de seguridad que escribe eventos a un archivo de log. Registra: login exitoso, login fallido, cambio de contraseña, solicitud de reset. Los emails se redactan parcialmente (c***@gmail.com) por privacidad. |
| `utils/limiter.py` | Instancia de SlowAPI (rate limiter). Limita peticiones por dirección IP. Se usa en los endpoints de auth para prevenir fuerza bruta. |

#### Migraciones Alembic (`be/alembic/versions/`)

Las migraciones son scripts que crean/modifican las tablas de la base de datos de forma incremental y reversible.

| # | Archivo | ¿Qué crea? |
|---|---------|-------------|
| 1 | `eeee1c29cefa_create_users...` | Tablas `users` y `password_reset_tokens`. La base para autenticación. |
| 2 | `fb563e20cc8e_add_domain_tables` | Todas las tablas de dominio ganadero: `department`, `purpose`, `role`, `city`, `farm`, `user_farm`, `land_plot`, `paddock`, `bovine`, `food`, `consumption`, `treatment`, `milk_production`, `task` y más. |
| 3 | `a1b2c3d4e5f6_add_views_and_functions` | 5 vistas SQL (`v_farm_summary`, `v_milk_production_daily`, `v_low_stock_alerts`, `v_pending_tasks`, `v_bovine_census`) y 2 funciones SQL (`fn_farm_statistics`, `fn_bovine_weight_history`). |
| 4 | `9d8e7f6a5b4c_seed_departments...` | Inserta los 33 departamentos de Colombia con códigos DANE. Cambia la columna de ciudad a texto libre. |
| 5 | `c1d2e3f4a5b6_add_security_consent...` | Agrega campos de seguridad a `users` (email_verified, token_version, consentimientos). Crea tablas `email_verification_tokens` y `audit_log`. |
| 6 | `e1f2a3b4c5d6_seed_roles_and_permissions` | Inserta los 4 roles (Administrador, Capataz, Veterinario, Empleado) con 32 permisos (8 módulos × 4 acciones CRUD). |

### 4.4. Frontend (`fe/`)

#### Infraestructura

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `fe/Dockerfile` | Construye la imagen en dos etapas: Node 20 compila la app React con Vite → nginx sirve los archivos estáticos (imagen final ~23 MB). |
| `fe/nginx.conf` | Configuración de nginx: sirve la SPA (Single Page Application) con fallback a `index.html` para que React Router funcione, y reenvía las peticiones `/api/` al backend. |
| `fe/package.json` | Dependencias: React 18, React Router 6, Axios, TypeScript 5, Tailwind CSS 4, Vite 5, Vitest. Scripts: `dev`, `build`, `test`, `lint`, `format`. |
| `fe/vite.config.ts` | Configuración de Vite (bundler): plugins React y Tailwind, puerto 5173, JSDOM para tests. |
| `fe/index.html` | HTML base. Monta `<div id="root">` donde React renderiza toda la aplicación. |

#### Código fuente React (`fe/src/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `src/main.tsx` | Punto de entrada. Renderiza `<App />` dentro de `React.StrictMode`. Importa los estilos globales. |
| `src/App.tsx` | **Enrutador principal.** Define todas las rutas: 7 públicas (`/`, `/login`, `/register`, `/forgot-password`, `/reset-password`, `/terms`, `/privacy`) y 3 protegidas (`/dashboard`, `/farms/new`, `/farms/:farmId`). Las protegidas están envueltas en `ProtectedRoute` + `AppLayout`. |
| `src/index.css` | Importa Tailwind CSS 4 y define la paleta de colores del proyecto: verde primario `#59930a`, verde claro `#a0b53a`, dorado `#e4da7e`, crema `#f8efbc`, superficie `#f8efeb`. |

#### Context y Hooks (Estado global)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `src/context/authContextDef.ts` | Define el `createContext` de React para autenticación. Separado para evitar dependencias circulares. |
| `src/context/AuthContext.tsx` | **`AuthProvider`** — Gestiona todo el estado de autenticación: `user`, `accessToken`, `refreshToken` (en sessionStorage). Provee funciones: `login()`, `register()` (con auto-login), `logout()`, `forgotPassword()`, `resetPassword()`. Al montar, verifica si hay una sesión existente llamando a `GET /users/me`. |
| `src/hooks/useAuth.ts` | Hook `useAuth()` — Atajo para consumir el AuthContext desde cualquier componente. Lanza error si se usa fuera de `AuthProvider`. |

#### API (comunicación con backend)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `src/api/axios.ts` | Crea una instancia de Axios pre-configurada. **Interceptor de request:** agrega automáticamente el header `Authorization: Bearer <token>` a toda petición. **Interceptor de response:** traduce errores del backend (422 de Pydantic, mensajes, etc.) a mensajes legibles. |
| `src/api/auth.ts` | Funciones HTTP para autenticación: `registerUser()`, `loginUser()`, `refreshToken()`, `forgotPassword()`, `resetPassword()`, `getMe()`. |
| `src/api/farms.ts` | Funciones HTTP para fincas: `createFarm()`, `listFarms()`, `getFarm()`, `listDepartments()`, `listPurposes()`. |
| `src/types/auth.ts` | Interfaces TypeScript: `RegisterRequest`, `LoginRequest`, `UserResponse`, `TokenResponse`, `MessageResponse`, `AuthContextType`, etc. |

#### Componentes reutilizables (`src/components/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `components/ProtectedRoute.tsx` | **Guard de ruta.** Si el usuario no está autenticado, redirige a `/login`. Si está cargando, muestra un spinner. Si está autenticado, renderiza los children (la página protegida). |
| `components/layout/AppLayout.tsx` | **Layout de páginas protegidas.** Estructura: Navbar sticky (logo, link "Mis Fincas" con resaltado de ruta activa, nombre+rol del usuario, botón cerrar sesión) → Breadcrumbs → Contenido de la página → Footer. |
| `components/layout/AuthLayout.tsx` | **Layout de páginas de autenticación.** Estructura: Header con logo y botón de acción → Contenido (formulario centrado) → Footer. Diseño de fondo con gradiente. |
| `components/layout/Header.tsx` | Header público con logo BoviTrack. Si recibe props (`actionLabel`, `actionTo`) muestra un solo botón. Si no, muestra dos: "Iniciar sesión" y "Registrarse". |
| `components/layout/Footer.tsx` | Footer verde con copyright, número de contacto y enlaces a Términos y Privacidad. |
| `components/layout/Breadcrumbs.tsx` | Muestra la ruta de navegación jerárquica. Ejemplo: `Inicio / Detalle de Finca`. Se oculta en el dashboard (ya estás en inicio). |

#### Páginas (`src/pages/`)

| Archivo | Ruta | ¿Qué muestra? |
|---------|------|----------------|
| `pages/HomePage.tsx` | `/` | Landing pública: hero con gradiente, 4 características (fincas, hato, producción, sanidad), sección "3 pasos", estadísticas, CTA final. |
| `pages/LoginPage.tsx` | `/login` | Formulario de login (email + contraseña). Valida frontend. Muestra banner si vienes de registro exitoso. Al enviar → `useAuth().login()` → redirige a `/dashboard`. |
| `pages/RegisterPage.tsx` | `/register` | Formulario completo: nombres, documento (5 tipos), email, teléfono, contraseña con indicador de fortaleza en vivo (5 niveles), confirmar contraseña, checkboxes de términos y datos personales. Auto-login post-registro. |
| `pages/ForgotPasswordPage.tsx` | `/forgot-password` | Solicita email. Siempre muestra éxito (no revela si el email existe = protección contra enumeración). Opción de reenviar. |
| `pages/ResetPasswordPage.tsx` | `/reset-password` | Lee token de la URL (`?token=xxx`). Formulario de nueva contraseña con barra de fortaleza y toggle de visibilidad. |
| `pages/DashboardPage.tsx` | `/dashboard` | Saludo personalizado + rol. Botón "Crear finca". Lista de fincas como cards con nombre, dirección, área e ID. Estado vacío con CTA. |
| `pages/CreateFarmPage.tsx` | `/farms/new` | Formulario: nombre, dirección, departamento (catálogo dinámico de 33 dptos), ciudad (texto libre), área + unidad, propósito (catálogo), identificador, teléfono. Vista de éxito post-creación. |
| `pages/FarmDetailPage.tsx` | `/farms/:farmId` | Detalle de finca: nombre, dirección, ciudad, departamento, área, teléfono, estado, fechas. |
| `pages/TermsPage.tsx` | `/terms` | Términos y condiciones (8 secciones). Cumple leyes colombianas 527/1999, 1480/2011, 1581/2012. |
| `pages/PrivacyPage.tsx` | `/privacy` | Política de privacidad (7+ secciones). Ley 1581/2012 Habeas Data: derechos ARCO, medidas de seguridad. |

### 4.5. Documentación (`docs/`)

| Archivo | ¿Para qué sirve? |
|---------|-------------------|
| `docs/BoviTrack.postman_collection.json` | Colección de Postman lista para importar. Tiene variables predefinidas y auto-guarda tokens al hacer login. |
| `docs/LISTA_CHEQUEO_COMPONENTES.md` | Lista de chequeo con el estado de cumplimiento de cada aspecto evaluable del proyecto. |
| `docs/RESUMEN_TECNICO_PROYECTO_ACTUAL.md` | Resumen ejecutivo del stack, modelos, endpoints y arquitectura. |
| `docs/GUIA_MIGRACIONES_ALEMBIC.md` | Guía paso a paso de cómo usar Alembic para crear y aplicar migraciones. |
| `docs/Estructura_Frontend_Registro.md` | Documentación específica del formulario de registro y sus validaciones. |
| `docs/HUs/` | 16 Historias de Usuario (HU001–HU016). |
| `docs/RF/` | 35 Requisitos Funcionales (RF001–RF035). |
| `docs/RNF/` | 12 Requisitos No Funcionales (RNF001–RNF012). |

---

## 5. Cómo funciona cada punto de la lista de chequeo

### 1. Base de Datos

#### 1.1 — La BD es funcional con tablas y tipos coherentes

PostgreSQL 17 con **19 modelos ORM** que crean **18+ tablas**. Cada tabla tiene tipos de datos apropiados:
- `UUID` para identificadores (no se repiten nunca, ni entre servidores)
- `String` con longitudes máximas para texto
- `Numeric` para áreas y cantidades
- `DateTime` con `server_default=now()` para timestamps automáticos
- `Boolean` para estados (is_active, email_verified)

**Dónde verlo:** `be/app/models/` → Cada archivo `.py` define clases que se mapean a tablas SQL.

#### 1.2 — Integridad referencial (PKs, FKs, UNIQUEs)

- **PKs UUID** en todas las tablas (generados con `uuid4()`)
- **Foreign Keys:** `user_id → users.id`, `farm_id → farm.id`, `role_id → role.id`, etc.
- **ON DELETE CASCADE:** Si borras un usuario, se borran sus tokens. Si borras una finca, se borran sus bovinos.
- **ON DELETE RESTRICT:** No puedes borrar un rol si hay usuarios asignados a él.
- **UNIQUE:** `email`, `document_number`, `token`, `farm_identifier`. Constraint compuesto `user_id + farm_id` en `user_farm` para evitar doble asignación.

**Dónde verlo:** `be/app/models/user.py` → `UniqueConstraint`, `ForeignKey`, `relationship()`.

#### 1.3 — Información pertinente y coherente

Las tablas cubren todo el dominio ganadero colombiano:
- Autenticación: `users`, `password_reset_tokens`, `email_verification_tokens`
- Gestión: `farm`, `bovine`, `paddock`, `land_plot`
- Producción: `milk_production`, `food`, `consumption`
- Sanidad: `treatment`
- Operación: `task`
- Seguridad: `role`, `permission`, `user_farm`, `audit_log`
- Catálogos: `department` (33 dptos de Colombia), `city`, `purpose`

#### 1.4 — Vistas y funciones SQL

Creadas en la migración `a1b2c3d4e5f6`:

| Vista/Función | ¿Qué hace? |
|---------------|-------------|
| `v_farm_summary` | Resumen por finca: total bovinos, potreros, área |
| `v_milk_production_daily` | Producción de leche agrupada por día y finca |
| `v_low_stock_alerts` | Alimentos con stock por debajo del nivel de alerta |
| `v_pending_tasks` | Tareas pendientes con fecha límite próxima |
| `v_bovine_census` | Censo de bovinos por sexo, estado y propósito |
| `fn_farm_statistics(UUID)` | Retorna JSON con estadísticas completas de una finca |
| `fn_bovine_weight_history(UUID)` | Retorna historial de pesos de un bovino |

**Cómo probarlo:** En Swagger, `GET /api/v1/farms/{farm_id}/statistics` llama a `fn_farm_statistics`.

#### 1.5 — Control de duplicidad

Doble barrera:
1. **BD:** Constraints UNIQUE → si se intenta insertar un email duplicado, PostgreSQL rechaza la operación
2. **Servicio:** Antes de insertar, `auth_service.py` consulta si ya existe un usuario con ese email o documento

**Dónde verlo:** `be/app/services/auth_service.py` → `register_user()` hace `SELECT` antes de `INSERT`.

#### 1.6 — Timestamps y auditoría

- Todas las tablas principales tienen `created_at` y `updated_at`
- Tabla `audit_log` registra: usuario, acción, entidad, ID, detalles JSON, timestamp
- Campos `accepted_terms_at` y `accepted_data_policy_at` en `users`
- Logger de seguridad escribe a archivo: login exitoso, fallido, cambios de contraseña

**Dónde verlo:** `be/app/services/audit_service.py`, `be/app/utils/audit_log.py`.

---

### 2. Frontend

#### 2.1 — Pantalla de inicio (Home)

`pages/HomePage.tsx` → Landing page con 5 secciones: hero, características, pasos, estadísticas, CTA.

**Cómo probarlo:** Abrir `http://localhost:5173/`.

#### 2.2 — Dashboard según rol

`pages/DashboardPage.tsx` → Muestra saludo con nombre del usuario, su rol (si tiene finca), y la lista de sus fincas como cards.

**Cómo probarlo:** Registrarse → crear finca → ver dashboard con rol "Administrador".

#### 2.3 — Header, footer y navegación

- **Header público** (`Header.tsx`): logo + botones login/registro
- **Navbar autenticado** (`AppLayout.tsx`): logo, "Mis Fincas", nombre+rol, cerrar sesión
- **Footer** (`Footer.tsx`): copyright, contacto, enlaces legales

#### 2.4 — Nombre y rol del usuario visible

En `AppLayout.tsx`, el navbar muestra `{first_name} {last_name}` y `Rol: {role_name}`. Los datos vienen de `GET /users/me` que busca el rol en `UserFarm → Role`.

#### 2.5 — Diseño consistente

Paleta definida en `index.css` con variables CSS que Tailwind consume. `AuthLayout` para páginas públicas, `AppLayout` para protegidas.

#### 2.6 — UI amigable

Tailwind CSS 4 con buen contraste, tipografías system-ui, emojis como iconos (🐄🏡🥛💊). Variables CSS para colores consistentes.

#### 2.7 — Responsive (RWD)

Breakpoints de Tailwind: `sm` (640px), `lg` (1024px). Grid de fincas: 1 col → 2 col → 3 col. Formulario de registro: 2 col → 1 col en mobile.

**Cómo probarlo:** Abrir DevTools del navegador (F12) → Toggle device toolbar (Ctrl+Shift+M) → Cambiar tamaño.

#### 2.8 — Componentes adecuados

Formularios con validación en tiempo real, select dropdowns, toggle show/hide password, cards para fincas, `ProtectedRoute` como guard de rutas.

#### 2.9 — Formularios con labels, placeholders, asteriscos

Todos los formularios tienen labels descriptivos, asteriscos rojos `*` en campos obligatorios, y placeholders de ayuda.

#### 2.10 — Validaciones en tiempo real

En `RegisterPage.tsx`: indicadores ✓/✗ por cada requisito de contraseña (8 chars, mayúscula, minúscula, número, especial), barra de fortaleza con 5 niveles y colores, regex para nombres (solo letras y tildes).

**Cómo probarlo:** Ir a `/register` y empezar a escribir una contraseña.

#### 2.11 — Mensajes de error y confirmación

- Errores: texto rojo debajo de cada campo + banner de error del servidor
- Éxito: redirección post-login, confirmaciones con emojis (✉️, ✅)
- Carga: textos dinámicos en botones ("Registrando...", "Ingresando...", "Creando finca...")

#### 2.12 — Tablas con paginación (PENDIENTE ❌)

No hay componentes de tabla en el frontend. Los endpoints del backend sí soportan filtros.

#### 2.13 — Breadcrumbs y ruta activa

`Breadcrumbs.tsx` muestra la ruta jerárquica (Inicio > Nueva Finca / Detalle de Finca). En `AppLayout.tsx`, el link "Mis Fincas" se resalta con borde inferior verde cuando estás en `/dashboard` o `/farms/*`.

**Cómo probarlo:** Navegar a una finca → ver breadcrumbs arriba del contenido y "Mis Fincas" resaltado.

#### 2.14 — Regla del tercer clic

- Home → Login → Dashboard: 2 clics
- Dashboard → Crear finca: 1 clic
- Dashboard → Detalle finca: 1 clic

#### 2.15 — Carga dinámica (SPA)

React Router maneja la navegación sin recargar la página. Axios hace peticiones HTTP asíncronas.

---

### 3. Backend

#### 3.1 — API REST documentada

40+ endpoints organizados en 10 routers con tags. Documentación generada automáticamente:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

#### 3.2 — Reglas de negocio

- Auth: tokens con expiración, password reset de un solo uso, token_version para invalidar sesiones
- Fincas: asignación automática de rol al crear
- Alimentos: validación de stock antes de consumir
- Auditoría: registro de acciones críticas

#### 3.3 — Validaciones Pydantic

Cada endpoint tiene schemas de request y response. Pydantic valida automáticamente tipos, longitudes, formatos, y retorna 422 con detalles del error.

**Cómo probarlo:** En Swagger, intentar enviar un registro con email inválido → verás el error detallado.

#### 3.4 — Manejo de excepciones

| Código HTTP | Significado | Ejemplo |
|-------------|-------------|---------|
| 201 | Creado exitosamente | Registro, crear finca |
| 400 | Datos inválidos | Email duplicado, stock insuficiente |
| 401 | No autenticado | Token expirado o inválido |
| 403 | Sin permiso | Rol sin acceso al módulo |
| 404 | No encontrado | Finca no existe |
| 409 | Conflicto | Duplicado |
| 422 | Error de validación Pydantic | Campo obligatorio faltante |
| 429 | Demasiados intentos | Rate limit excedido |

#### 3.5 — CRUD en cada módulo

8 módulos con CRUD completo: fincas, bovinos, tratamientos, producción de leche, alimentos + consumos, tareas, potreros. Users tiene GET + DELETE.

#### 3.6 — Reportes parametrizados

5 endpoints de reportes que consumen vistas y funciones SQL. Filtros por `farm_id`.

#### 3.7 — Cargas masivas

`POST /api/v1/farms/bulk` acepta un array de fincas y las crea todas en una transacción.

#### 3.8 — Tiempo de respuesta

FastAPI con Uvicorn es extremadamente rápido. SQLAlchemy con pool de conexiones. Sin operaciones bloqueantes.

---

### 4. Seguridad

#### 4.1 — Registro con validaciones

Email único (BD + servicio). Contraseña: mín 8 chars + mayúscula + minúscula + número + especial. Documento único. Consentimientos obligatorios.

#### 4.2 — Encriptación de contraseñas (bcrypt)

`passlib` con esquema bcrypt. La contraseña NUNCA se guarda en texto plano. `hash_password()` al registrar, `verify_password()` al hacer login.

**Dónde verlo:** `be/app/utils/security.py`.

#### 4.3 — Verificación de email (parcial)

Endpoint implementado. Token se genera al registrar. En desarrollo imprime el enlace en consola. Para producción solo falta configurar SMTP en `.env`.

#### 4.4 — Login con JWT

`POST /auth/login` → valida email + contraseña con bcrypt → genera access token (15 min) + refresh token (7 días) → frontend los guarda en sessionStorage.

#### 4.5 — Tokens seguros

- JWT firmados con HS256 y SECRET_KEY
- Access token: 15 minutos de vida
- Refresh token: 7 días de vida
- Campo `token_version` para invalidación masiva (logout-all)

#### 4.6 — Rate limiting

`slowapi` limita peticiones por IP:
- Registro: 5/minuto
- Login: 10/minuto
- Forgot password: 3/minuto
- Respuesta 429 si se excede

**Cómo probarlo:** Hacer 11 login seguidos rápido → recibirás error 429.

#### 4.7 — Recuperación de contraseña

Flujo completo: forgot-password → email con token UUID → reset-password con token + nueva contraseña. Token válido 1 hora, de un solo uso. Siempre retorna éxito para no revelar si el email existe.

#### 4.8 — Roles y permisos RBAC

4 roles predefinidos con 32 permisos (8 módulos × 4 acciones):

| Rol | Acceso |
|-----|--------|
| **Administrador** | CRUD total en todos los módulos |
| **Capataz** | Crear y leer todo, actualizar, no puede eliminar |
| **Veterinario** | Enfocado en bovinos y tratamientos |
| **Empleado** | Solo lectura en la mayoría de módulos |

**Dónde verlo:** Migración `e1f2a3b4c5d6_seed_roles_and_permissions.py`.

#### 4.9 — Rutas protegidas

- **Backend:** `get_current_user()` valida JWT en cada endpoint protegido. `require_permission()` verifica RBAC.
- **Frontend:** `ProtectedRoute` redirige a login si no hay sesión.

#### 4.10 — Auditoría

Tabla `audit_log` registra acciones de CRUD sobre fincas. Logger de seguridad registra eventos de autenticación a archivo.

#### 4.11 — Invalidación de tokens al cerrar sesión

`POST /auth/logout-all` incrementa `token_version` del usuario. `get_current_user()` compara la versión del token JWT con la de la BD. Si no coincide, el token es inválido.

#### 4.12 — Protección OWASP Top 10

| Amenaza OWASP | Cómo se protege |
|----------------|-----------------|
| **A01 Broken Access Control** | RBAC con 4 roles + 32 permisos, `require_permission()` en cada endpoint |
| **A02 Cryptographic Failures** | bcrypt para passwords, JWT firmado con secreto en `.env` |
| **A03 Injection** | SQLAlchemy ORM (queries parametrizadas, nunca SQL crudo) |
| **A04 Insecure Design** | Rate limiting, tokens con expiración, protección contra enumeración |
| **A05 Security Misconfiguration** | CORS con origin específico, security headers, usuario no-root en Docker |
| **A07 Auth Failures** | JWT con expiración corta, rate limit en login, token_version |
| **A09 Security Logging** | audit_log en BD + logger a archivo |

#### 4.13 — HTTPS (pendiente)

nginx escucha en HTTP (puerto 80). Para producción se necesita configurar certificados SSL.

---

### 5. Experiencia de Usuario

#### 5.1 — Mensajes claros de error y éxito

Errores por campo en rojo, banners de error del servidor, estados de carga en botones. Rate limit: "Demasiados intentos".

#### 5.2 — Confirmaciones por correo (parcial)

Confirmación visual en todas las operaciones. Correo para reset password (en consola). SMTP pendiente de configurar.

#### 5.3 — Redirección automática

Registro → auto-login → dashboard. Login → dashboard.

#### 5.4 — Cerrar sesión en todos los dispositivos

`POST /logout-all` invalida todos los tokens existentes incrementando `token_version`.

#### 5.5 — Eliminar cuenta con confirmación doble

`DELETE /users/me` requiere enviar `{ "confirmation_text": "ELIMINAR" }`. Hace soft delete (is_active = false).

---

### 6. Cumplimiento Legal

#### 6.1 — Términos y privacidad visibles

Checkboxes obligatorios en registro. Páginas `/terms` y `/privacy` con contenido legal completo. Enlaces en el footer.

#### 6.2 — Consentimiento de datos personales

Checkbox separado: "Autorizo el tratamiento de mis datos personales". No se puede registrar sin aceptar. Se envía `accept_data_policy: true` al backend.

#### 6.3 — Registro de consentimientos

Campos en tabla `users`: `accepted_terms` (boolean), `accepted_data_policy` (boolean), `accepted_terms_at` (timestamp), `accepted_data_policy_at` (timestamp). Se persisten al momento del registro.

---

### 7. Gestión del Proyecto

#### 7.1 — Conocimiento técnico

Stack completo implementado: React+TS+Vite (FE), FastAPI+SQLAlchemy+Pydantic (BE), PostgreSQL+Alembic (BD), Docker Compose con 3 servicios.

#### 7.4 — Git

Repositorio en GitHub: `https://github.com/Tomas0512/BOVITRACK`. `.gitignore` configurado. Commits descriptivos.

---

### 8. Aspectos Técnicos Complementarios

#### 8.1 — Validaciones Pydantic

Pydantic valida automáticamente los datos de entrada en cada endpoint. Si un campo está mal, FastAPI retorna error 422 con detalle exacto del problema.

```python
# Ejemplo en schemas/user.py
class UserCreate(BaseModel):
    email: EmailStr               # Valida formato email
    password: str                 # min 8, mayúsc, minúsc, dígito, especial
    first_name: str               # min 2, max 255, solo letras
    accept_terms: bool            # Debe ser True
```

#### 8.2 — Migraciones Alembic con ORM y relaciones

Alembic lee los modelos SQLAlchemy y genera scripts SQL automáticamente. Las 6 migraciones se ejecutan en orden y son reversibles.

```bash
# Ver estado actual de migraciones
docker exec bovitrack_be alembic current

# Aplicar todas las migraciones pendientes
docker exec bovitrack_be alembic upgrade head

# Revertir la última migración
docker exec bovitrack_be alembic downgrade -1
```

#### 8.3 — ORM (Object Relational Mapping)

SQLAlchemy mapea clases Python a tablas SQL. En lugar de escribir SQL crudo, escribes código Python:

```python
# En vez de: SELECT * FROM users WHERE email = 'x@y.com'
stmt = select(User).where(User.email == "x@y.com")
user = db.execute(stmt).scalar_one_or_none()
```

Beneficios: previene SQL Injection, código más legible, cambios de esquema gestionados con migraciones.

#### 8.4 — Versionado de API

Todos los endpoints bajo `/api/v1/`. Si necesitas cambios incompatibles, creas `/api/v2/` sin romper la versión anterior.

#### 8.5 — OpenAPI / Swagger

FastAPI genera documentación interactiva automáticamente basada en los schemas Pydantic y los type hints de Python.

---

## 6. Cómo probar con Swagger (OpenAPI)

Swagger es una interfaz web que te permite probar los endpoints directamente desde el navegador.

### Acceder a Swagger

1. Asegúrate de que Docker esté corriendo (`docker compose up -d`)
2. Abre `http://localhost:8000/docs` en el navegador
3. Verás todos los endpoints agrupados por tags

### Probar el flujo de autenticación

**Paso 1 — Registrar un usuario:**

1. Busca `POST /api/v1/auth/register` → haz clic → "Try it out"
2. Pega este JSON:
```json
{
  "email": "camilo@test.com",
  "first_name": "Camilo",
  "last_name": "Ortiz",
  "document_type": "CC",
  "document_number": "1234567890",
  "phone": "3001234567",
  "password": "MiClave123!",
  "accept_terms": true,
  "accept_data_policy": true
}
```
3. Haz clic en "Execute" → deberías ver respuesta 201

**Paso 2 — Iniciar sesión:**

1. Busca `POST /api/v1/auth/login` → "Try it out"
2. Pega:
```json
{
  "email": "camilo@test.com",
  "password": "MiClave123!"
}
```
3. En la respuesta, copia el valor de `access_token`

**Paso 3 — Autenticarte en Swagger:**

1. Haz clic en el botón verde "Authorize" 🔒 (arriba a la derecha)
2. Pega el access_token que copiaste
3. Clic en "Authorize" → ahora TODOS los endpoints enviarán tu token automáticamente

**Paso 4 — Probar endpoints protegidos:**

- `GET /api/v1/users/me` → ver tu perfil
- `POST /api/v1/farms/` → crear una finca
- `GET /api/v1/farms/` → listar tus fincas
- `GET /api/v1/farms/{farm_id}/statistics` → estadísticas de finca

---

## 7. Cómo probar con Postman

### Importar la colección

1. Abre Postman
2. Haz clic en "Import" (arriba a la izquierda)
3. Arrastra el archivo `docs/BoviTrack.postman_collection.json`
4. Se importará con variables y endpoints pre-configurados

### Variables de la colección

| Variable | Valor por defecto | ¿Para qué? |
|----------|-------------------|-------------|
| `base_url` | `http://localhost:8000` | URL base del backend |
| `access_token` | (vacío) | Se llena automáticamente al hacer login |
| `refresh_token` | (vacío) | Se llena automáticamente al hacer login |

### Flujo de prueba recomendado

1. **Health Check:** `GET {{base_url}}/` → debe retornar `{"status": "ok"}`
2. **Registrar:** `POST {{base_url}}/api/v1/auth/register` → crear usuario
3. **Login:** `POST {{base_url}}/api/v1/auth/login` → los tokens se guardan automáticamente en las variables de la colección
4. **Mi perfil:** `GET {{base_url}}/api/v1/users/me` → usa el token auto-guardado
5. **Crear finca:** `POST {{base_url}}/api/v1/farms/` → con datos de la finca
6. **Listar fincas:** `GET {{base_url}}/api/v1/farms/`
7. **Ver detalle:** `GET {{base_url}}/api/v1/farms/{id}`

### ¿Cómo funciona la autenticación automática en Postman?

En la petición de Login, hay un script Post-response que guarda automáticamente los tokens:

```javascript
// Se ejecuta después de recibir la respuesta del login
var jsonData = pm.response.json();
pm.collectionVariables.set("access_token", jsonData.access_token);
pm.collectionVariables.set("refresh_token", jsonData.refresh_token);
```

Las demás peticiones incluyen en el header:
```
Authorization: Bearer {{access_token}}
```

Así no tienes que copiar y pegar el token manualmente cada vez.

---

## 8. Cómo probar desde el navegador (Frontend)

### Flujo completo de prueba

1. **Abre** `http://localhost:5173` → verás la HomePage (landing)
2. **Regístrate:** clic en "Registrarse" → llena el formulario → observa las validaciones en vivo
3. **Dashboard:** después del registro, serás redirigido automáticamente al dashboard
4. **Crear finca:** clic en "+ Crear finca" → llena el formulario (el departamento se carga de la BD)
5. **Ver finca:** clic en la card de la finca → verás el detalle
6. **Breadcrumbs:** observa arriba "Inicio / Detalle de Finca" con enlace clickeable
7. **Navbar activa:** observa que "Mis Fincas" está resaltado en verde
8. **Cerrar sesión:** clic en "Cerrar sesión" → vuelves al login
9. **Probar login:** ingresa con tu email y contraseña → vuelves al dashboard
10. **Responsive:** abre DevTools (F12) → Ctrl+Shift+M → cambia el tamaño → verás el diseño adaptarse

### Probar protección de rutas

- Si cierras sesión e intentas ir a `http://localhost:5173/dashboard` → serás redirigido a `/login`
- Si borras los tokens de sessionStorage (DevTools → Application → Session Storage → Clear) → al recargar irás a login

### Probar recuperación de contraseña

1. En login, clic "¿Olvidaste tu contraseña?"
2. Ingresa el email → verás mensaje de éxito (aunque el email no exista, por seguridad)
3. El enlace de reset aparece en los logs del backend: `docker compose logs be -f`
4. Copia la URL del log y ábrela en el navegador → formulario de nueva contraseña

---

## 9. Glosario técnico

| Término | Significado |
|---------|-------------|
| **API REST** | Interfaz de programación basada en HTTP. Cada URL (endpoint) representa un recurso y los métodos HTTP (GET, POST, PUT, DELETE) representan acciones. |
| **JWT (JSON Web Token)** | Token firmado digitalmente que contiene datos del usuario (ID, expiración). El backend lo genera al hacer login y el frontend lo envía en cada petición. |
| **bcrypt** | Algoritmo de hashing irreversible para contraseñas. No se puede "descifrar", solo se puede verificar si un texto coincide con el hash. |
| **ORM (Object Relational Mapping)** | Técnica que mapea tablas SQL a clases Python. En vez de escribir SQL, trabajas con objetos. SQLAlchemy es el ORM que usa BoviTrack. |
| **Pydantic** | Librería de validación de datos para Python. Define "schemas" que FastAPI usa para validar entrada/salida automáticamente. |
| **Alembic** | Herramienta de migraciones de base de datos. Genera scripts que crean/modifican tablas de forma incremental y reversible. |
| **RBAC (Role-Based Access Control)** | Control de acceso basado en roles. Cada usuario tiene un rol por finca, y cada rol tiene permisos específicos sobre cada módulo. |
| **CORS (Cross-Origin Resource Sharing)** | Mecanismo de seguridad del navegador. El backend debe declarar qué dominios pueden hacer peticiones. |
| **Rate Limiting** | Límite de peticiones por tiempo. Protege contra fuerza bruta (muchos intentos de login seguidos). |
| **SPA (Single Page Application)** | Aplicación que carga una sola vez y luego navega sin recargar la página, usando JavaScript para cambiar el contenido. |
| **Docker Compose** | Herramienta para definir y ejecutar aplicaciones multi-contenedor. Un archivo define todos los servicios y sus relaciones. |
| **Swagger / OpenAPI** | Especificación estándar para documentar APIs REST. FastAPI la genera automáticamente desde el código. |
| **Soft Delete** | Eliminación lógica: en vez de borrar el registro de la BD, se marca como inactivo (`is_active = false`). Se puede recuperar. |
| **Interceptor (Axios)** | Función que se ejecuta antes de cada petición (para agregar el token) o después de cada respuesta (para manejar errores). |
| **OWASP Top 10** | Lista de las 10 vulnerabilidades de seguridad web más críticas. Es el estándar de referencia para seguridad de aplicaciones. |
| **Middleware** | Código que se ejecuta ANTES de que la petición llegue al endpoint. Se usa para CORS, headers de seguridad, rate limiting. |

---

*Informe técnico generado el 26 de marzo de 2026 para el proyecto BoviTrack — SENA.*
