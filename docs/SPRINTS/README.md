# Plan de Sprints de Cierre - BoviTrack

Fecha de ultima actualizacion: 17-06-2026
Regla de planificacion: 15 dias por sprint, asignacion vertical (cada persona dueña de su HU completa).
Equipo: 3 personas (Camilo Ortiz, Tomas Canon, Edwin Delgado).

## Roles

1. **Tomas Canon** — Full-stack (Developer / Product Owner)
2. **Edwin Delgado** — Full-stack (Developer)
3. **Camilo Ortiz** — Full-stack (Developer / Scrum Master) + QA

## Flujo de trabajo por ramas

Cada sprint se trabaja con **ramas individuales por persona**. Nadie toca la rama de otro.

| Quién | Rama |
|-------|------|
| Tomas | `feature/sprint{N}-tomas` |
| Edwin | `feature/sprint{N}-edwin` |
| Camilo | `feature/sprint{N}-camilo` |

- **Documentacion (`docs/SPRINTS/`)** se actualiza directo en `main`
- **Codigo** se trabaja en cada rama y se hace merge a `main` al final del sprint

## Estado real por HU (15-06-2026)

| HU | Estado | Observaciones |
|----|--------|---------------|
| HU001 | ✅ Completa | Autenticacion JWT, RBAC, 4 roles, 32 permisos |
| HU002 | ✅ Completa | Fincas y lotes (backend + frontend) |
| HU003 | ✅ Completa | Potreros (backend + frontend) |
| HU004 | ✅ Completa | Registro y gestion de bovinos |
| HU005 | ✅ Completa | Alimentacion, ordenos, pesajes, graficas (Recharts) |
| HU006 | ✅ Completa | Control reproductivo, auto-ternero y timeline funcionales |
| HU007 | ✅ Completa | CalfList, GrowthChart, CRUD terneros (Sprint 6 — Camilo) |
| HU008 | ✅ Completa | Planes sanitarios, alertas, calendario (cerrado en Sprint 4) |
| HU009 | ✅ Completa | Movimientos de animales (Sprint 6/7 — Tomas) |
| HU010 | ✅ Completa | Modelo economico, CRUD, indicadores, dashboard (Sprint 6 — Edwin) |
| HU011 | ✅ Completa | Inventario, compras, alertas stock bajo (Sprint 7 — Edwin) |
| HU012 | ✅ Completa | Gestion documental, upload/download (Sprint 7 — Camilo) |
| HU013 | ✅ Completa | Reportes PDF/Excel con filtros (Sprint 7 — Tomas) |
| HU014 | 🔲 Pendiente | Fuera del alcance de Sprints 1-7 |
| HU015 | 🔲 Pendiente | Fuera del alcance de Sprints 1-7 |
| HU016 | 🔲 Pendiente | Fuera del alcance de Sprints 1-7 |

## Plan restante (asignacion vertical)

| Sprint | Fechas | Tomas | Edwin | Camilo |
|--------|--------|-------|-------|--------|
| **Sprint 5** | May 30 - Jun 12 | ✅ HU005 cierre + HU006.5 timeline | ✅ HU006 backend + HU006.4 auto-ternero | ✅ QA |
| **Sprint 6** | Jun 13 - 26 | ✅ HU009 completo | ✅ HU010 completo | ✅ HU007 completo |
| **Sprint 7** | Jun 27 - Jul 10 | ✅ HU013 — Reportes | ✅ HU011 — Inventarios | ✅ HU012 — Gestion documental |
| | *(completado anticipadamente el 17 de junio)* | | | |

Total 6 sprints. Sin dependencias entre personas dentro del mismo sprint (asignacion vertical).
