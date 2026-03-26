# Resumen Tecnico Actual del Proyecto BoviTrack

Fecha: 18 de marzo de 2026

## 1. Que es BoviTrack hoy

BoviTrack es un sistema para gestion ganadera, pero el desarrollo implementado actualmente esta concentrado en el modulo de autenticacion de usuarios.

Hoy el sistema ya permite:

1. Registro de usuario.
2. Inicio de sesion con JWT.
3. Renovacion de tokens con refresh token.
4. Flujo de olvide mi contrasena.
5. Restablecimiento de contrasena con token temporal.
6. Despliegue con Docker Compose de frontend, backend y base de datos.

Referencia general: [README](../README.md)

## 2. Arquitectura y funcionamiento general

El proyecto corre en tres servicios orquestados por Docker Compose:

1. Base de datos PostgreSQL en [docker-compose.yml](../docker-compose.yml).
2. Backend FastAPI en [docker-compose.yml](../docker-compose.yml).
3. Frontend React compilado y servido por Nginx en [docker-compose.yml](../docker-compose.yml).

Flujo de una peticion tipica:

1. El usuario entra por http://localhost:5173.
2. El frontend lo sirve Nginx segun [fe/nginx.conf](../fe/nginx.conf).
3. Si la app llama rutas de API, Nginx proxia /api hacia el backend.
4. FastAPI recibe la solicitud en [be/app/main.py](../be/app/main.py).
5. FastAPI valida datos con esquemas Pydantic en [be/app/schemas/user.py](../be/app/schemas/user.py).
6. La logica de negocio se ejecuta en [be/app/services/auth_service.py](../be/app/services/auth_service.py).
7. SQLAlchemy persiste o consulta en PostgreSQL usando [be/app/database.py](../be/app/database.py) y modelos ORM.
8. El backend responde al frontend y la UI actualiza el estado sin recargar pagina.

## 3. Frontend: que hay y para que sirve

Carpeta principal: [fe/src](../fe/src)

### 3.1 Entrada y ruteo

1. [fe/src/main.tsx](../fe/src/main.tsx): punto de entrada de React.
2. [fe/src/App.tsx](../fe/src/App.tsx): define rutas de autenticacion.

Rutas actuales:

1. /register
2. /login
3. /forgot-password
4. /reset-password
5. / redirige a /register

### 3.2 Capa de llamadas HTTP

1. [fe/src/api/auth.ts](../fe/src/api/auth.ts): cliente Axios y funciones para endpoints de autenticacion.

Funciones implementadas:

1. registerUser
2. loginUser
3. forgotPassword
4. resetPassword

### 3.3 Paginas implementadas

1. [fe/src/pages/RegisterPage.tsx](../fe/src/pages/RegisterPage.tsx): formulario de registro con validaciones de nombres, correo, contrasena y confirmacion.
2. [fe/src/pages/LoginPage.tsx](../fe/src/pages/LoginPage.tsx): login y guardado de access_token y refresh_token en localStorage.
3. [fe/src/pages/ForgotPasswordPage.tsx](../fe/src/pages/ForgotPasswordPage.tsx): solicitud de enlace de recuperacion por correo.
4. [fe/src/pages/ResetPasswordPage.tsx](../fe/src/pages/ResetPasswordPage.tsx): cambio de contrasena con token de URL.

### 3.4 Layout y estilo

1. [fe/src/components/layout/AuthLayout.tsx](../fe/src/components/layout/AuthLayout.tsx): estructura comun de paginas de auth.
2. [fe/src/components/layout/Header.tsx](../fe/src/components/layout/Header.tsx): logo y boton de accion.
3. [fe/src/components/layout/Footer.tsx](../fe/src/components/layout/Footer.tsx): pie de pagina legal y de contacto.
4. [fe/src/index.css](../fe/src/index.css): variables de color y estilos globales.

### 3.5 Configuracion y build frontend

1. [fe/vite.config.ts](../fe/vite.config.ts): configuracion de Vite y tests.
2. [fe/Dockerfile](../fe/Dockerfile): build multi-stage para compilar React y servir con Nginx.
3. [fe/nginx.conf](../fe/nginx.conf): soporte SPA y proxy de API.
4. [fe/package.json](../fe/package.json): scripts y dependencias.

### 3.6 Estado funcional del frontend

1. Existe el modulo de autenticacion completo en UI.
2. Aun no existe dashboard funcional.
3. Carpetas [fe/src/context](../fe/src/context), [fe/src/hooks](../fe/src/hooks) y [fe/src/types](../fe/src/types) estan en estado base con .gitkeep.

## 4. Backend: que hay y para que sirve

Carpeta principal: [be/app](../be/app)

### 4.1 Entrada y configuracion

1. [be/app/main.py](../be/app/main.py): app FastAPI, CORS, routers y health endpoint.
2. [be/app/config.py](../be/app/config.py): carga y validacion de variables de entorno con pydantic-settings.
3. [be/app/database.py](../be/app/database.py): engine SQLAlchemy, sesiones y Base ORM.
4. [be/app/dependencies.py](../be/app/dependencies.py): dependencias de DB y autenticacion por token.

### 4.2 API de autenticacion

Archivo principal: [be/app/routers/auth.py](../be/app/routers/auth.py)

Endpoints actuales:

1. POST /api/v1/auth/register
2. POST /api/v1/auth/login
3. POST /api/v1/auth/refresh
4. POST /api/v1/auth/forgot-password
5. POST /api/v1/auth/reset-password

### 4.3 Logica de negocio

Archivo principal: [be/app/services/auth_service.py](../be/app/services/auth_service.py)

Funciones clave:

1. register_user
2. login_user
3. refresh_access_token
4. request_password_reset
5. reset_password

### 4.4 Modelos y validaciones

1. [be/app/models/user.py](../be/app/models/user.py): tabla users.
2. [be/app/models/password_reset_token.py](../be/app/models/password_reset_token.py): tabla de tokens de recuperacion.
3. [be/app/schemas/user.py](../be/app/schemas/user.py): validaciones de request/response con Pydantic.

### 4.5 Utilidades de seguridad y correo

1. [be/app/utils/security.py](../be/app/utils/security.py): hashing bcrypt, creacion y validacion de JWT.
2. [be/app/utils/email.py](../be/app/utils/email.py): envio de correo de recuperacion en modo desarrollo (log de enlace).

### 4.6 Migraciones y configuracion de Alembic

1. [be/alembic/env.py](../be/alembic/env.py): integra Alembic con modelos y settings.
2. [be/alembic/versions/eeee1c29cefa_create_users_and_password_reset_tokens_.py](../be/alembic/versions/eeee1c29cefa_create_users_and_password_reset_tokens_.py): migracion inicial.
3. [be/alembic.ini](../be/alembic.ini): configuracion de Alembic.

## 5. Base de datos: que hay y como funciona

### 5.1 Motor y arranque

1. PostgreSQL corre como servicio db en [docker-compose.yml](../docker-compose.yml).
2. [db/Dockerfile](../db/Dockerfile): imagen de la base.
3. [db/init.sql](../db/init.sql): habilita extension uuid-ossp y valida inicializacion.

### 5.2 Esquema actual

La migracion inicial crea:

1. Tabla users.
2. Tabla password_reset_tokens.
3. Indices unicos para email, document_number y token.
4. Llave foranea user_id con eliminacion en cascada.

Fuente: [be/alembic/versions/eeee1c29cefa_create_users_and_password_reset_tokens_.py](../be/alembic/versions/eeee1c29cefa_create_users_and_password_reset_tokens_.py)

## 6. Seguridad actual implementada

1. Contrasenas hasheadas con bcrypt.
2. Access token y refresh token con expiracion.
3. Validacion fuerte de contrasena en frontend y backend.
4. Prevencion de enumeracion de usuarios en forgot-password (respuesta generica).
5. Token de recuperacion de un solo uso con expiracion.
6. CORS con origen permitido configurado por FRONTEND_URL.
7. Backend en contenedor ejecutando como usuario no root.
8. Base de datos no expuesta por puerto al host en compose.

Archivos de referencia:

1. [be/app/utils/security.py](../be/app/utils/security.py)
2. [be/app/services/auth_service.py](../be/app/services/auth_service.py)
3. [be/app/main.py](../be/app/main.py)
4. [be/Dockerfile](../be/Dockerfile)

## 7. Riesgos y pendientes de seguridad

1. No hay logout con invalidacion de tokens.
2. No hay blacklist ni rotacion de refresh tokens.
3. No hay rate limiting ni bloqueo por intentos fallidos.
4. Tokens se guardan en localStorage.
5. No hay roles y permisos todavia.
6. No hay auditoria de acciones criticas.
7. No hay HTTPS configurado para produccion.
8. Envio SMTP real aun no habilitado (modo desarrollo/log).

## 8. Infraestructura y despliegue

Archivo principal: [docker-compose.yml](../docker-compose.yml)

Servicios:

1. db: PostgreSQL con volumen persistente y healthcheck.
2. be: FastAPI en puerto 8000.
3. fe: Nginx sirviendo frontend, publicado en 5173 hacia el host.

Imagenes:

1. [be/Dockerfile](../be/Dockerfile): multi-stage backend + healthcheck.
2. [fe/Dockerfile](../fe/Dockerfile): multi-stage frontend con Nginx.

Variables de entorno:

1. [../.env.example](../.env.example)
2. [be/.env.example](../be/.env.example)
3. [fe/.env.example](../fe/.env.example)

## 9. Estado de pruebas y calidad

### 9.1 Frontend

1. Pruebas ejecutan con Vitest.
2. Actualmente fallan pruebas en [fe/src/App.test.tsx](../fe/src/App.test.tsx) porque esperan contenido antiguo que ya no coincide con la app actual.
3. Archivo de setup [fe/src/__tests__/setup.ts](../fe/src/__tests__/setup.ts) esta vacio.

### 9.2 Backend

1. No hay casos de prueba implementados aun.
2. La carpeta de tests existe, pero sin pruebas funcionales.

## 10. Resumen ejecutivo

El proyecto tiene una base tecnica solida para autenticacion y despliegue con contenedores. La arquitectura esta bien separada por capas y el flujo principal funciona de extremo a extremo.

Lo siguiente para evolucionar el producto es:

1. Implementar dashboard y modulos de negocio ganadero.
2. Incorporar roles y permisos.
3. Fortalecer seguridad operativa (logout real, rate limiting, hardening).
4. Completar estrategia de pruebas frontend y backend.
