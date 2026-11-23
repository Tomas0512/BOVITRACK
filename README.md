# 🐄 BoviTrack

> Sistema de control y registro de ganado bovino para fincas ganaderas.

BoviTrack nace de la necesidad del ganadero Luis Barbosa de digitalizar la gestión de su hato con una herramienta intuitiva, segura y accesible tanto para el dueño como para sus empleados. Reemplaza los registros manuales con una aplicación móvil que centraliza el historial productivo, sanitario y reproductivo de cada animal.

---

## 📋 Tabla de Contenidos

- [Stack](#stack)
- [Módulos del sistema](#módulos-del-sistema)
- [Requisitos previos](#requisitos-previos)
- [Inicio rápido con Docker](#inicio-rápido-con-docker-recomendado)
- [Desarrollo local](#desarrollo-local-sin-docker)
- [Comandos útiles](#comandos-útiles)
- [Integración continua (CI)](#integración-continua-ci)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Convenciones](#convenciones)
- [Documentación adicional](#documentación-adicional)
- [Propósito educativo](#propósito-educativo)
- [Exención de responsabilidades](#exención-de-responsabilidades)
- [Licencia](#licencia)
- [Integrantes](#integrantes)

---

## Stack

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic |
| **Frontend** | React 18+, Vite, TypeScript, TailwindCSS 4 |
| **Base de datos** | PostgreSQL 17 (Docker) |
| **Testing** | Selenium E2E activo (`qa_e2e/`) + verificación manual de API; pytest (BE) y Vitest (FE) configurados para suites de unidad/cobertura |
| **Linting** | Ruff (BE), ESLint + Prettier (FE) |

## Módulos del sistema

- **Gestión de usuarios y accesos** — roles: Administrador, Capataz, Veterinario, Empleado
- **Fincas y lotes** — registro de fincas, lotes y potreros
- **Animales** — identificación, genealogía, trazabilidad completa
- **Sanidad** — vacunaciones, desparasitaciones, tratamientos y calendario sanitario
- **Reproducción** — servicios, diagnósticos, partos y seguimiento de gestación
- **Producción** — ordeño diario, pesajes y alimentación por lote
- **Inventario** — insumos, compras y consumos con control de stock
- **Economía** — ingresos, egresos e indicadores de rentabilidad
- **Reportes** — exportables en PDF y Excel con paneles interactivos
- **Documentos** — adjuntar archivos a fincas
- **Alertas** — alertas de stock bajo de alimentos y notificaciones configurables por usuario (canal correo/in-app, eventos y frecuencia) con historial de envíos
- **Auditoría** — consulta filtrable por usuario, acción, entidad, finca y rango de fechas, con paginación y exportación en CSV/Excel

## Requisitos previos

| Herramienta | Versión mínima | Notas |
|-------------|---------------|-------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24+ | Incluye Docker Compose v2 |
| [Git](https://git-scm.com/) | cualquiera | Para clonar el repo |
| [Node.js](https://nodejs.org/) | 22+ | Solo para desarrollo local del frontend |
| [Python](https://www.python.org/) | 3.12+ | Solo para desarrollo local del backend |

> Con Docker no se necesita Node.js ni Python instalados localmente.

---

## Inicio rápido con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd bovitrack

# 2. Crear el archivo de variables de entorno
cp .env.example .env
# Editar .env con los valores reales (usuario, contraseña, secret key, etc.)

# 3. Levantar todos los servicios
# Las migraciones de Alembic se ejecutan automáticamente al iniciar el backend.
docker compose up -d --build
```

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend (Swagger UI) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 (solo acceso local) |

Para detener:
```bash
docker compose down
```

Para detener y borrar los datos de la base de datos:
```bash
docker compose down -v
```

---

## Desarrollo local (sin Docker)

### Backend

```bash
cd be
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash / PowerShell)
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
# Editar .env con los valores reales
alembic upgrade head
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000` — Swagger UI en `http://localhost:8000/docs`

### Frontend

```bash
# Habilitar corepack (una sola vez por máquina)
corepack enable

cd fe
pnpm install
cp .env.example .env
# Editar .env con los valores reales
pnpm dev
```

## Comandos útiles

### Backend (dentro de `be/`)

```bash
pip install . --group dev                    # Dependencias de la app + herramientas
ruff check app tests                         # Linting
ruff format .                                # Formato
lint-imports                                 # Contratos de arquitectura (fronteras entre módulos)
alembic upgrade head && alembic check        # Migraciones y modelos == BD
pytest -q --cov=app --cov-report=term        # Tests con cobertura
```

### Frontend (dentro de `fe/`)

```bash
pnpm lint          # ESLint con fronteras de features (--max-warnings 0)
pnpm test          # Vitest (incluye la prueba de estructura src/test/architecture.test.ts)
pnpm test:coverage # Tests con cobertura
pnpm build         # tsc + Vite (build de producción)
pnpm format        # Formato con Prettier
```

### Producción

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Ver [docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md](docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md) (sección 1.1).

## Integración continua (CI)

Cada push (a `main`, `refactor/**`, `feature/**`, `fix/**`, `chore/**`) y cada pull request a `main`
corre [.github/workflows/ci.yml](.github/workflows/ci.yml) en GitHub Actions. Si un job falla, el PR lo muestra
con el paso y el error.

| Job | Qué verifica |
|-----|--------------|
| **Backend** | `ruff`, contratos de `import-linter`, migraciones en un PostgreSQL 17 limpio, `alembic check` (modelos == BD), deshacer **todas** las migraciones hasta una BD vacía y volver a aplicarlas, y `pytest` con cobertura |
| **Frontend** | `pnpm install --frozen-lockfile`, ESLint sin avisos, Vitest y `pnpm build` |
| **Stack de producción** | Construye las imágenes, levanta `docker-compose.prod.yml` hasta que todo esté *healthy* y comprueba: la web responde 200, la API detrás de nginx responde 401 sin sesión, y `/docs` y `/openapi.json` dan 404 |

Para reproducirlo en local antes de subir, corre los comandos de **Comandos útiles** (backend y frontend).

> **Regla para migraciones nuevas:** cada migración define sus tablas y columnas de forma explícita
> (`op.create_table`, `op.add_column`…) y su `downgrade()` deshace **solo** lo que ella creó. Nunca usar
> `Base.metadata.create_all()`/`drop_all()` ni importar modelos dentro de una migración: el resultado cambiaría
> cada vez que cambie un modelo y la cadena dejaría de poder deshacerse. CI lo comprueba con `alembic downgrade base`.

## Estructura del proyecto

El backend es un **monolito modular por capas** y el frontend está organizado **por features**. Cada módulo
y cada feature tiene su propio `README.md` con su responsabilidad, su contrato público y sus fronteras.

```
bovitrack/
├── .github/workflows/ci.yml              # Integración continua (backend, frontend, stack de producción)
├── .env.example                          # Plantilla de variables de entorno
├── docker-compose.yml                    # Desarrollo (db, be con --reload, fe)
├── docker-compose.prod.yml               # Producción (solo nginx expuesto, volúmenes persistentes)
├── docs/                                 # Documentación (HUs, RF, RNF, sprints, despliegue, Postman)
├── db/                                   # Imagen PostgreSQL 17 + init.sql (uuid-ossp)
├── be/                                   # Backend — FastAPI + Python
│   ├── app/
│   │   ├── main.py                       # Composición: crea la app y monta los routers de los módulos
│   │   ├── core/                         # Infraestructura: config, BD, seguridad, correo, límites, errores
│   │   ├── shared/                       # Lo común a todos: excepciones de dominio, puertos, tipos
│   │   └── modules/                      # 14 módulos de negocio (identity, farms, livestock, health, ...)
│   │       └── <modulo>/                 # router → dependencies → service → schemas → repository → models
│   │                                     # API pública en __init__.py; README.md por módulo
│   ├── alembic/                          # Migraciones de base de datos
│   ├── tests/                            # Tests con pytest
│   ├── entrypoint.sh                     # Migra y arranca uvicorn (modo dev o producción)
│   └── pyproject.toml                    # Dependencias, ruff y contratos de import-linter
├── fe/                                   # Frontend — React + Vite + TypeScript
│   ├── src/
│   │   ├── app/                          # Composición: App, rutas, layout y páginas hub
│   │   ├── core/http/                    # Cliente HTTP y manejo de sesión
│   │   ├── shared/                       # UI, hooks, tema y layout reutilizables
│   │   ├── features/<feature>/           # Una carpeta por feature (api, componentes, páginas, tipos)
│   │   └── test/                         # Setup de Vitest y prueba de estructura
│   ├── nginx.conf                        # Sirve la SPA y proxia /api al backend
│   └── package.json
├── qa_e2e/                               # Pruebas E2E — Selenium WebDriver + Python
└── mobile/                               # App móvil — React Native + Expo
```

Las fronteras se hacen cumplir con herramientas, no solo con convenciones: `lint-imports` en el backend y
ESLint (`no-restricted-imports`) + `architecture.test.ts` en el frontend. Ver
[be/app/modules/README.md](be/app/modules/README.md) y [fe/src/README.md](fe/src/README.md).

---

## Convenciones

| Aspecto | Regla |
|---------|-------|
| Nomenclatura técnica | Inglés (variables, funciones, clases, endpoints) |
| Comentarios y docs | Español |
| Commits | Conventional Commits en inglés (`feat:`, `fix:`, `chore:`, etc.) |
| Python | PEP 8 + type hints obligatorios + ruff |
| TypeScript | strict mode + ESLint + Prettier |
| Gestor de paquetes Node | `pnpm` — **nunca npm ni yarn** |
| Gestor de paquetes Python | `venv` |
| Testing | Todo código nuevo debe tener tests |

---

## Documentación adicional

| Documento | Descripción |
|-----------|-------------|
| [docs/RESUMEN_TECNICO_PROYECTO_ACTUAL.md](docs/RESUMEN_TECNICO_PROYECTO_ACTUAL.md) | Resumen técnico del estado actual del proyecto |
| [docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md](docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md) | Desarrollo vs. producción (`docker-compose.prod.yml`), Cloudflare Tunnel y alternativa Supabase |
| [be/app/modules/README.md](be/app/modules/README.md) | Arquitectura del backend: módulos, capas y contratos |
| [fe/src/README.md](fe/src/README.md) | Arquitectura del frontend: features y fronteras |
| [docs/PRUEBAS_BD/](docs/PRUEBAS_BD/) | Evidencia de pruebas de base de datos (Guía 6): matriz BD vs. aplicación y script SQL CP01–CP27 |
| [docs/HUs/](docs/HUs/) | Historias de Usuario (HU001 – HU016) |
| [docs/RF/](docs/RF/) | Requisitos Funcionales (RF001 – RF035) |
| [docs/RNF/](docs/RNF/) | Requisitos No Funcionales (RNF001 – RNF012) |
| [docs/SPRINTS/](docs/SPRINTS/) | Planificación y seguimiento de Sprints |
| [docs/BoviTrack.postman_collection.json](docs/BoviTrack.postman_collection.json) | Colección Postman con todos los endpoints |

---

## Propósito educativo

Este proyecto es desarrollado como ejercicio formativo en el marco del **SENA**. Cada módulo, endpoint y componente está diseñado para aplicar buenas prácticas reales de desarrollo de software: separación de responsabilidades, seguridad, testing y documentación.

---

## Exención de responsabilidades

Este proyecto es de naturaleza **exclusivamente educativa**.

- **No apto para producción** sin una revisión de seguridad profesional previa.
- **Credenciales de ejemplo** en `.env.example` son solo ilustrativas. Nunca usarlas en producción.
- **Sin garantía de disponibilidad** — puede contener bugs propios de un entorno de aprendizaje.

---

## Licencia

[![CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Licenciado bajo **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International**.
Ver [LICENSE](./LICENSE) para más información.

---

## Integrantes

| # | Nombre | Documento |
|---|--------|-----------|
| 1 | Camilo Andrés Ortiz Arévalo |
| 2 | Tomás Alejandro Cañón Moreno |
| 3 | Edwin Nicolas Delgado Arboleda |
