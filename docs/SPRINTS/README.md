# Plan de Sprints de Cierre - BoviTrack

Fecha de corte del analisis: 15-06-2026
Regla de planificacion: 15 dias por sprint, asignacion vertical (cada persona dueña de su HU completa).
Equipo: 2 personas activas (Tomas Canon, Edwin Delgado). Camilo Ortiz fuera del equipo.

## Roles

1. **Tomas Canon** — Full-stack (Developer / Product Owner)
2. **Edwin Delgado** — Full-stack (Developer)

## Flujo de trabajo por ramas

Cada sprint se trabaja con **ramas individuales por persona**. Nadie toca la rama de otro.

| Quién | Rama |
|-------|------|
| Tomas | `feature/sprint{N}-tomas` |
| Edwin | `feature/sprint{N}-edwin` |

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
| HU007 | 🔲 Pendiente | Desarrollo de terneros — sin responsable (era de Camilo) |
| HU008 | ✅ Completa | Planes sanitarios, alertas, calendario (cerrado en Sprint 4) |
| HU009 | 🔲 Pendiente | Para completar en Sprint 6 por Tomas |
| HU010 | 🔲 Pendiente | Para completar en Sprint 6 por Edwin |
| HU011 | 🔲 Parcial | Pendiente cierre de compras/costos (→ Sprint 7 Edwin) |
| HU012 | 🔲 Pendiente | Gestion documental — sin responsable (era de Camilo) |
| HU013 | 🔲 Parcial | Endpoints existen, falta exportacion + frontend (→ Sprint 7 Tomas) |
| HU014 | 🔲 Pendiente | Para completar en Sprint 8 por Tomas |
| HU015 | 🔲 Parcial | Auditoria existe, falta exportacion avanzada + UI (→ Sprint 8) |
| HU016 | 🔲 Pendiente | Para completar en Sprint 8 por Edwin |

## Plan restante (asignacion vertical — Camilo fuera del equipo)

| Sprint | Fechas | Tomas | Edwin |
|--------|--------|-------|-------|
| **Sprint 5** | May 30 - Jun 12 | ✅ HU005 cierre + HU006.5 timeline | ✅ HU006 backend + HU006.4 auto-ternero |
| **Sprint 6** | Jun 13 - 26 | **HU009** — Movimientos animales | **HU010** — Informacion economica |
| **Sprint 7** | Jun 27 - Jul 10 | **HU013** — Reportes (cierre) | **HU011** — Inventarios (cierre) |
| **Sprint 8** | Jul 11 - 24 | **HU014** — Alertas/notificaciones | **HU016** — Offline (backend) |
| **Sprint 9** | Jul 25 - Ago 7 | QA final, regresion, bugs, estabilizacion (todos) | |
| **Sprint 10** | Ago 8 - 21 | Cierre proyecto, demo final, despliegue, retrospectiva (todos) | |

Total 6 sprints. Sin dependencias entre personas dentro del mismo sprint (asignacion vertical).
