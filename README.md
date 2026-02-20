# 🐄 BoviTrack

> Sistema de control y registro de ganado bovino para fincas ganaderas.

BoviTrack nace de la necesidad del ganadero Luis Barbosa de digitalizar la gestión de su hato con una herramienta intuitiva, segura y accesible tanto para el dueño como para sus empleados. Reemplaza los registros manuales con una aplicación móvil que centraliza el historial productivo, sanitario y reproductivo de cada animal.

## Stack

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic |
| **Frontend** | React 18+, Vite, TypeScript, TailwindCSS 4 |
| **Base de datos** | PostgreSQL 17 (Docker) |
| **Testing** | pytest + pytest-cov (BE), Vitest + Testing Library (FE) |
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
- **Alertas** — notificaciones automáticas por correo y WhatsApp
- **Documentos** — adjuntar archivos a animales, fincas o eventos
- **Auditoría** — registro automático de acciones de usuarios
- **Modo offline** — registro sin conexión con sincronización automática

## Levantar la base de datos

```bash
docker compose up -d
```

## Backend

```bash
cd be
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000` — Swagger UI en `http://localhost:8000/docs`

## Frontend

```bash
cd fe
pnpm install
cp .env.example .env
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

## Integrantes

| # | Nombre | Documento |
|---|--------|-----------|
| 1 | Camilo Andrés Ortiz Arévalo | 1000159472 |
| 2 | Tomás Alejandro Cañón Moreno | 1027401323 |

