# Plan de Sprints de Cierre - BoviTrack

Fecha de ultima actualizacion: 07-08-2026
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

## Estado real por HU (07-08-2026)

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
| HU014 | 🔨 En curso | Alertas y notificaciones — Sprint 8 (Final) — Tomas |
| HU015 | 🔨 En curso | Auditorias del sistema — Sprint 8 (Final) — Camilo |
| HU016 | 🚫 Fuera de alcance | Modo offline (movil) — pospuesto por fecha limite 23/08; ver Sprint 8 |

## Plan restante (asignacion vertical)

| Sprint | Fechas | Tomas | Edwin | Camilo |
|--------|--------|-------|-------|--------|
| **Sprint 5** | May 30 - Jun 12 | ✅ HU005 cierre + HU006.5 timeline | ✅ HU006 backend + HU006.4 auto-ternero | ✅ QA |
| **Sprint 6** | Jun 13 - 26 | ✅ HU009 completo | ✅ HU010 completo | ✅ HU007 completo |
| **Sprint 7** | Jun 27 - Jul 10 | ✅ HU013 — Reportes | ✅ HU011 — Inventarios | ✅ HU012 — Gestion documental |
| | *(completado anticipadamente el 17 de junio)* | | | |
| **Sprint 8 (Final)** | Ago 8 - 23 | ✅/🔲 HU014 — Alertas | 🔲 QA y cierre web (HU001–HU013) | 🔲 HU015 — Auditorias |

> **Reprogramacion 07-08-2026:** Los Sprints 9 y 10 originales fueron **absorbidos en el Sprint 8 (Final)** por la fecha limite real del 23 de agosto. El Sprint 8 incluye construccion de HU014 + HU015, QA de regresion y cierre del desarrollo web (ver [SPRINT_08.md](./SPRINT_08.md)). HU016 (offline) queda fuera de alcance. No hay despliegue en produccion; se cierra con demo funcional en Docker.

Total: 8 sprints planificados (Sprints 1-7 cerrados + Sprint 8 Final). Sin dependencias entre personas dentro del mismo sprint (asignacion vertical).
