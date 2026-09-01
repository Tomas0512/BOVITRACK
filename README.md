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

### Backend

```bash
pytest -v                          # Correr tests
pytest --cov=app --cov-report=term-missing  # Tests con cobertura
ruff check .                       # Linting
ruff format .                      # Formato
```

### Frontend

```bash
pnpm test          # Correr tests
pnpm test:coverage # Tests con cobertura
pnpm lint          # Linting
pnpm format        # Formato con Prettier
```

## Estructura del proyecto

```
bovitrack/
├── .env.example                          # Plantilla de variables de entorno
├── docker-compose.yml                    # Orquesta los tres servicios (db, be, fe)
├── README.md                             # Este archivo
├── docs/                                 # Documentación del proyecto
│   ├── HUs/                              # Historias de Usuario
│   ├── RF/                               # Requisitos Funcionales
│   ├── RNF/                              # Requisitos No Funcionales
│   ├── SPRINTS/                          # Planificación de Sprints
│   ├── interview/                        # Entrevistas con el cliente
│   ├── BoviTrack.postman_collection.json # Colección de endpoints para Postman
│   └── RESUMEN_TECNICO_PROYECTO_ACTUAL.md
├── db/                                   # Base de datos
│   ├── Dockerfile                        # Imagen PostgreSQL 17 con uuid-ossp
│   └── init.sql                          # Script de inicialización
├── be/                                   # Backend — FastAPI + Python
│   ├── app/
│   │   ├── main.py                       # Punto de entrada FastAPI
│   │   ├── config.py                     # Configuración (Pydantic Settings)
│   │   ├── database.py                   # Conexión a PostgreSQL
│   │   ├── models/                       # Modelos ORM (SQLAlchemy)
│   │   ├── schemas/                      # Schemas Pydantic
│   │   ├── routers/                      # Endpoints de la API
│   │   ├── services/                     # Lógica de negocio
│   │   ├── utils/                        # Utilidades
│   │   └── tests/                        # Tests con pytest
│   ├── alembic/                          # Migraciones de base de datos
│   └── requirements.txt
├── fe/                                   # Frontend — React + Vite + TypeScript
│   ├── src/
│   │   ├── api/                          # Clientes HTTP
│   │   ├── components/                   # Componentes reutilizables
│   │   ├── pages/                        # Vistas/páginas
│   │   ├── hooks/                        # Custom hooks
│   │   ├── context/                      # Context providers
│   │   └── types/                        # Tipos TypeScript
│   └── package.json
├── qa_e2e/                                 # Pruebas E2E — Selenium WebDriver + Python
│   ├── base_test.py                        # Clase base: driver, login y screenshots
│   ├── config.py                           # URL, credenciales e IDs de prueba
│   ├── test_01..15_*.py                    # 15 vistas x 2 casos de uso
│   ├── run_all_tests.py                    # Ejecuta toda la suite
│   └── screenshots/                        # Evidencia gráfica generada
└── mobile/                               # App móvil — React Native + Expo
    └── src/
        ├── navigation/                   # Navegación (React Navigation)
        ├── screens/                      # Pantallas
        ├── services/                     # Servicios y llamadas a la API
        ├── store/                        # Estado global
        ├── theme/                        # Estilos y tema
        └── types/                        # Tipos TypeScript
```

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
| [docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md](docs/DESPLIEGUE_Y_INFRAESTRUCTURA.md) | Guía de despliegue en línea (Cloudflare Tunnel) y alternativa Supabase |
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
