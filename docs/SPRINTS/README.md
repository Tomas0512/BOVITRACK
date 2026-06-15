# Plan de Sprints de Cierre - BoviTrack

Fecha de corte del analisis: 15-06-2026
Regla de planificacion: 15 dias por sprint, asignacion vertical (cada persona dueña de su HU completa).
Equipo: 3 personas (Camilo Ortiz, Tomas Canon, Edwin Delgado).

## Roles

1. **Tomas Canon** — Full-stack (Developer / Product Owner)
2. **Edwin Delgado** — Full-stack (Developer)
3. **Camilo Ortiz** — Full-stack (Developer / Scrum Master) + QA

## Estado real por HU (15-06-2026)

| HU | Estado | Observaciones |
|----|--------|---------------|
| HU001 | ✅ Completa | Autenticacion JWT, RBAC, 4 roles, 32 permisos |
| HU002 | ✅ Completa | Fincas y lotes (backend + frontend) |
| HU003 | ✅ Completa | Potreros (backend + frontend) |
| HU004 | ✅ Completa | Registro y gestion de bovinos |
| HU005 | ✅ Completa | Alimentacion, ordenos, pesajes, graficas (Recharts) |
| HU006 | ✅ Backend completo | Pendiente: auto-ternero, ReproductiveTimeline frontend, QA (→ Sprint 6) |
| HU007 | 🔲 Pendiente | Para completar en Sprint 6 por Camilo |
| HU008 | ✅ Completa | Planes sanitarios, alertas, calendario (cerrado en Sprint 4) |
| HU009 | 🔲 Pendiente | Para completar en Sprint 6 por Tomas |
| HU010 | 🔲 Pendiente | Para completar en Sprint 6 por Edwin |
| HU011 | 🔲 Parcial | Pendiente cierre de compras/costos (→ Sprint 7 Edwin) |
| HU012 | 🔲 Pendiente | Para completar en Sprint 7 por Camilo |
| HU013 | 🔲 Parcial | Endpoints existen, falta exportacion + frontend (→ Sprint 7 Tomas) |
| HU014 | 🔲 Pendiente | Para completar en Sprint 8 por Tomas |
| HU015 | 🔲 Parcial | Auditoria existe, falta exportacion avanzada + UI (→ Sprint 8 Camilo) |
| HU016 | 🔲 Pendiente | Para completar en Sprint 8 por Edwin + Camilo |

## Plan restante (asignacion vertical)

| Sprint | Fechas | Tomas | Edwin | Camilo |
|--------|--------|-------|-------|--------|
| **Sprint 5** | May 30 - Jun 12 | ✅ HU005 cierre (frontend) | ✅ HU006 backend | QA + filtros |
| **Sprint 6** | Jun 13 - 26 | **HU009** — Movimientos animales | **HU010** — Informacion economica | HU006 cierre + HU007 terneros + QA |
| **Sprint 7** | Jun 27 - Jul 10 | **HU013** — Reportes (cierre) | **HU011** — Inventarios (cierre) | HU012 — Gestion documental + QA |
| **Sprint 8** | Jul 11 - 24 | **HU014** — Alertas/notificaciones | **HU016** — Offline (backend) | HU015 auditoria + HU016 frontend + QA |
| **Sprint 9** | Jul 25 - Ago 7 | QA final, regresion, bugs, estabilizacion (todos) | | |
| **Sprint 10** | Ago 8 - 21 | Cierre proyecto, demo final, despliegue, retrospectiva (todos) | | |

Total 6 sprints. Sin dependencias entre personas dentro del mismo sprint (asignacion vertical).
