# Guía de Presentación — BoviTrack

## Estructura de la Presentación (15-20 minutos)

---

## 1. Introducción (2 min)

### Qué decir:

> "Buenas tardes. Somos Camilo Ortiz y Tomas Cañon. Nuestro proyecto se llama **BoviTrack**, un sistema web para la gestión integral de fincas ganaderas. Permite registrar fincas, bovinos, producción de leche, tratamientos sanitarios, tareas operativas, alimentos e inventario, y potreros. Fue desarrollado con React en el frontend, FastAPI en el backend, y PostgreSQL como base de datos, todo orquestado con Docker."

### Datos clave para mencionar:

- **19 modelos de base de datos** (18+ tablas)
- **40+ endpoints** REST organizados en 10 módulos
- **4 roles** con 32 permisos granulares (RBAC)
- **5 vistas SQL** y 2 funciones SQL para reportes
- **6 migraciones** Alembic secuenciales
- Cumple con **OWASP Top 10** (seguridad)
- Cumple con **Ley 1581/2012** (protección de datos)

---

## 2. Demo en vivo (8-10 min)

### Antes de la presentación:

1. Abre Docker Desktop
2. Ejecuta: `docker compose up -d --build`
3. Ejecuta: `docker exec bovitrack_be alembic upgrade head`
4. Verifica que funciona: abre `http://localhost:5173`
5. Abre también `http://localhost:8000/docs` (Swagger) en otra pestaña
6. Ten Postman abierto con la colección importada

### Flujo del demo:

#### Paso 1 — Home (Landing Page)
- Mostrar la página de inicio: "Esta es nuestra landing page pública. Tiene las características principales del sistema, los pasos para empezar, y los botones de acceso."

#### Paso 2 — Registro
- Hacer clic en "Registrarse"
- Mostrar las validaciones en tiempo real mientras escribes la contraseña: "Tenemos un indicador de fortaleza de contraseña con 5 niveles. Validamos en tiempo real: mayúsculas, minúsculas, números y caracteres especiales."
- Mostrar los checkboxes de términos: "Cumplimos con la Ley 1581 de protección de datos. El usuario debe aceptar términos y autorizar tratamiento de datos. Estos consentimientos se guardan en base de datos con timestamp."
- Completar el registro

#### Paso 3 — Dashboard
- "Después del registro, el sistema hace auto-login y redirige al dashboard. Aquí se muestra el nombre del usuario y su rol."
- "Como es un usuario nuevo sin fincas, no aparece rol todavía."

#### Paso 4 — Crear Finca
- Hacer clic en "Crear finca"
- Mostrar breadcrumbs: "Observen los breadcrumbs: Inicio > Nueva Finca"
- Mostrar el formulario: "Los departamentos se cargan dinámicamente de la base de datos — son los 33 departamentos de Colombia con códigos DANE."
- Crear la finca
- "Al crear la finca, se le asigna automáticamente el rol Administrador al creador. Esto es parte del sistema RBAC."

#### Paso 5 — Detalle de Finca
- Mostrar el detalle: "Vean cómo la navbar resalta 'Mis Fincas' en verde — eso es el estado activo del menú."
- Mostrar breadcrumbs: Inicio > Detalle de Finca

#### Paso 6 — Swagger (OpenAPI)
- Cambiar a la pestaña de Swagger: "FastAPI genera documentación automática. Todos nuestros 40+ endpoints están documentados aquí."
- Mostrar los tags: Auth, Usuarios, Fincas, Bovinos, Tratamientos, Producción de Leche, Alimentos, Tareas, Potreros, Reportes
- Hacer una petición desde Swagger: Autenticarse con el botón "Authorize" y llamar a GET /users/me

#### Paso 7 — Responsive
- Abrir DevTools (F12) → Toggle device (Ctrl+Shift+M)
- Mostrar en tamaño móvil: "El diseño es responsive. Los grids de fincas pasan de 3 columnas a 1, los formularios se reorganizan."

#### Paso 8 — Seguridad (si hay tiempo)
- Intentar ir a `/dashboard` sin sesión → muestra que redirige a login
- Mencionar: "Rate limiting: si alguien intenta hacer login más de 10 veces por minuto, el sistema lo bloquea temporalmente con error 429."

---

## 3. Explicación técnica (3-5 min)

### Arquitectura (dibujar en tablero si es posible):

```
Navegador → nginx (puerto 5173) → /api/ → FastAPI (puerto 8000) → PostgreSQL
                                 → /* → React SPA
```

### Frases clave para decir:

**Sobre la base de datos:**
> "Usamos PostgreSQL con SQLAlchemy como ORM. ORM significa Object Relational Mapping — en vez de escribir SQL crudo, trabajamos con clases Python que se mapean a tablas. Esto previene inyección SQL porque las queries son parametrizadas."

**Sobre las migraciones:**
> "Usamos Alembic para gestionar migraciones. Tenemos 6 migraciones que crean las tablas, vistas, funciones, y datos semilla como los departamentos y roles. Cada migración es reversible."

**Sobre la seguridad:**
> "Las contraseñas se hashean con bcrypt — nunca se guardan en texto plano. Usamos tokens JWT con expiración de 15 minutos para el access token y 7 días para el refresh. Tenemos rate limiting con SlowAPI para prevenir ataques de fuerza bruta."

**Sobre RBAC:**
> "Implementamos control de acceso basado en roles. Tenemos 4 roles: Administrador con acceso total, Capataz que puede crear y editar pero no eliminar, Veterinario enfocado en bovinos y tratamientos, y Empleado con solo lectura. Son 32 permisos distribuidos en 8 módulos."

**Sobre validaciones:**
> "Usamos Pydantic para validar todos los datos de entrada. Cada endpoint tiene schemas que definen exactamente qué campos son obligatorios, los tipos, longitudes máximas y formatos. Si algo no cumple, retorna error 422 automáticamente."

---

## 4. Preguntas frecuentes del evaluador

### Sobre la Base de Datos

**P: ¿Qué motor de base de datos usan y por qué?**
> "PostgreSQL 17. Lo elegimos porque es robusto, soporta UUID nativamente, tiene buen manejo de JSON y es el estándar de la industria para aplicaciones empresariales."

**P: ¿Cómo manejan la integridad referencial?**
> "Con llaves foráneas en todas las relaciones. Usamos ON DELETE CASCADE para relaciones dependientes como usuario→tokens, y ON DELETE RESTRICT para proteger datos como roles asignados. También tenemos constraints UNIQUE en email, documento y farm_identifier."

**P: ¿Tienen vistas o procedimientos almacenados?**
> "Sí, tenemos 5 vistas SQL: resumen de fincas, producción de leche diaria, alertas de stock bajo, tareas pendientes y censo de bovinos. Y 2 funciones SQL: estadísticas de finca que retorna JSON, e historial de peso de bovino."

**P: ¿Cómo controlan la duplicidad?**
> "Doble barrera: constraints UNIQUE en la base de datos y validación en la capa de servicio antes de insertar. Si alguien intenta registrarse con un email que ya existe, primero lo detecta el servicio, y si de alguna forma pasa, PostgreSQL lo rechaza."

**P: ¿Qué es Alembic?**
> "Es la herramienta de migraciones para SQLAlchemy. Genera scripts que crean o modifican tablas de forma incremental. Cada migración tiene upgrade (aplicar) y downgrade (revertir). Así controlamos la evolución del esquema de BD."

---

### Sobre el Backend

**P: ¿Qué es FastAPI?**
> "Es un framework de Python para crear APIs REST. Lo elegimos porque genera documentación automática (Swagger), valida datos con Pydantic, y es muy rápido. Cada endpoint recibe datos tipados y retorna respuestas tipadas."

**P: ¿Qué es un endpoint?**
> "Es una URL específica de la API que realiza una operación. Por ejemplo, POST /api/v1/auth/login es el endpoint para iniciar sesión. Tenemos más de 40 endpoints organizados en 10 módulos."

**P: ¿Qué es un router?**
> "Es un agrupador de endpoints relacionados. Por ejemplo, el router de fincas agrupa crear finca, listar fincas, editar finca y eliminar finca. Mantiene el código organizado por módulo."

**P: ¿Qué es CRUD?**
> "Create, Read, Update, Delete. Son las 4 operaciones básicas sobre datos. Lo implementamos en 8 módulos: fincas, bovinos, tratamientos, producción de leche, alimentos, consumos, tareas y potreros."

**P: ¿Qué es Pydantic y para qué lo usan?**
> "Es una librería de validación de datos. Definimos schemas que especifican la forma de los datos — tipos, longitudes, formatos. Por ejemplo, el schema de registro valida que el email tenga formato válido, que la contraseña tenga mínimo 8 caracteres con mayúsculas, minúsculas, números y especiales. Si algo no cumple, Pydantic retorna un error 422 automáticamente, sin que escribamos lógica de validación manual."

**P: ¿Cómo manejan los errores?**
> "Usamos HTTPException de FastAPI con códigos estándar: 400 para datos inválidos, 401 para no autenticado, 403 para sin permiso, 404 para no encontrado, 409 para duplicados, 422 para validación Pydantic, y 429 para rate limit excedido. Todos con mensajes descriptivos."

---

### Sobre Seguridad

**P: ¿Cómo protegen las contraseñas?**
> "Con bcrypt a través de passlib. La contraseña se hashea al registrar y solo se puede verificar, nunca descifrar. Además validamos fortaleza: mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial."

**P: ¿Cómo funciona la autenticación JWT?**
> "Al hacer login, el backend genera dos tokens firmados: un access token que dura 15 minutos y un refresh token que dura 7 días. El frontend guarda los tokens en sessionStorage y los envía en cada petición en el header Authorization. Cuando el access token expira, usa el refresh token para obtener uno nuevo."

**P: ¿Qué es RBAC?**
> "Role-Based Access Control — control de acceso basado en roles. Cada usuario tiene un rol por finca. Cada rol tiene permisos específicos. Cuando un usuario intenta, por ejemplo, eliminar un bovino, el sistema verifica: ¿este usuario tiene el permiso can_delete en el módulo bovinos dentro de esta finca?"

**P: ¿Cómo se protegen contra inyección SQL?**
> "Usamos SQLAlchemy como ORM. Las queries son parametrizadas — nunca concatenamos valores del usuario en SQL. SQLAlchemy traduce objetos Python a queries seguras."

**P: ¿Qué es OWASP?**
> "Es el Open Web Application Security Project. Publican el Top 10 de vulnerabilidades web más comunes. Nos protegemos contra varias: inyección SQL con ORM, autenticación rota con JWT y rate limiting, broken access control con RBAC, XSS con React que escapa contenido, y tenemos headers de seguridad como X-Frame-Options y X-Content-Type-Options."

**P: ¿Qué pasa si alguien intenta hacer muchos logins?**
> "Rate limiting con SlowAPI. El login está limitado a 10 intentos por minuto por IP. Si se excede, retorna error 429 Too Many Requests."

**P: ¿Cómo cierran sesión?**
> "Tenemos logout-all que incrementa el token_version del usuario en la BD. Cuando el backend valida un token, compara la versión del JWT con la de la BD. Si no coinciden, el token es inválido. Así se invalidan TODOS los tokens en todos los dispositivos."

---

### Sobre el Frontend

**P: ¿Qué tecnologías usan en el frontend?**
> "React 18 con TypeScript para tipado estático, Vite como bundler, Tailwind CSS 4 para estilos, React Router 6 para navegación, y Axios para peticiones HTTP."

**P: ¿Cómo manejan el estado de autenticación?**
> "Con React Context. El AuthProvider envuelve toda la app y provee funciones como login, register, logout. Los tokens se guardan en sessionStorage. Al recargar la página, verifica si hay una sesión existente llamando a GET /users/me."

**P: ¿Qué es una SPA?**
> "Single Page Application. La app se carga una sola vez y la navegación entre páginas se hace con JavaScript sin recargar. React Router maneja las rutas del lado del cliente."

**P: ¿Cómo protegen las rutas en el frontend?**
> "Con un componente ProtectedRoute que verifica si el usuario está autenticado. Si no lo está, redirige a /login. Si está cargando, muestra un spinner."

**P: ¿Cómo es responsive?**
> "Usamos Tailwind CSS con breakpoints: sm para pantallas pequeñas y lg para grandes. Los grids cambian de 1 a 2 a 3 columnas según el tamaño. Los formularios de registro pasan de 2 columnas a 1 en móvil."

---

### Sobre Docker y Arquitectura

**P: ¿Qué es Docker y por qué lo usan?**
> "Docker empaqueta cada servicio en un contenedor con todo lo que necesita. Así el proyecto funciona igual en cualquier computador. Con docker compose up -d levantamos los 3 servicios: base de datos, backend y frontend."

**P: ¿Qué es un contenedor?**
> "Es como una caja aislada que contiene la aplicación, sus dependencias y un sistema operativo mínimo. Funciona igual en Windows, Mac o Linux. Es más ligero que una máquina virtual."

**P: ¿Cuántos servicios tienen?**
> "Tres: fe (frontend con nginx), be (backend con FastAPI), y db (PostgreSQL). Se comunican por redes internas de Docker. La base de datos no está expuesta al exterior, solo el backend puede accederla."

---

### Sobre el Proyecto y Metodología

**P: ¿Qué metodología usan?**
> "SCRUM. Camilo es Product Owner y prioriza el backlog. Tomas es Scrum Master y facilita las ceremonias. Ambos somos desarrolladores Full-Stack."

**P: ¿Cómo usan Git?**
> "Control de versiones con GitHub. El repositorio está en github.com/Tomas0512/BOVITRACK. Hacemos commits descriptivos."

**P: ¿Cómo documentaron el proyecto?**
> "Tenemos 16 Historias de Usuario, 35 Requisitos Funcionales, 12 Requisitos No Funcionales, una lista de chequeo de componentes y un informe técnico completo. Todo en la carpeta docs/."

---

### Sobre Postman y Swagger

**P: ¿Qué es Swagger?**
> "Es una interfaz web que FastAPI genera automáticamente en /docs. Muestra todos los endpoints con sus parámetros y permite probarlos directamente desde el navegador. Se genera a partir del código — los schemas Pydantic y los type hints."

**P: ¿Qué es Postman?**
> "Es una aplicación para probar APIs. Seleccionas el método HTTP, escribes la URL, agregas datos y headers, y ves la respuesta. Tenemos una colección con todos los endpoints pre-configurados que se importa desde docs/BoviTrack.postman_collection.json."

**P: ¿Cómo prueban los endpoints?**
> "De dos formas: Swagger para pruebas rápidas en el navegador, y Postman para pruebas organizadas con variables. En la colección de Postman, al hacer login los tokens se guardan automáticamente en variables para las demás peticiones."

---

## 5. Errores comunes durante la presentación

| Problema | Solución rápida |
|----------|-----------------|
| Docker no arranca | Abrir Docker Desktop, esperar que cargue, luego `docker compose up -d --build` |
| "Error de servidor" al registrar | `docker exec bovitrack_be alembic upgrade head` (las migraciones no se aplicaron) |
| Puerto 5173 ocupado | `docker compose stop fe` y luego levantar de nuevo |
| "Finca no encontrada" | Verificar que se aplicaron todas las migraciones |
| La página no carga | Verificar contenedores: `docker ps` — deben estar los 3 "Up" |

---

## 6. Checklist pre-presentación

- [ ] Docker Desktop abierto y corriendo
- [ ] `docker compose up -d --build` ejecutado
- [ ] `docker exec bovitrack_be alembic upgrade head` ejecutado
- [ ] `http://localhost:5173` abre la landing page
- [ ] `http://localhost:8000/docs` abre Swagger
- [ ] Postman abierto con la colección importada
- [ ] Base de datos limpia (o con un usuario de prueba listo)
- [ ] DevTools del navegador cerradas (las abres solo cuando muestras responsive)
- [ ] Este documento abierto en el celular para consulta rápida
