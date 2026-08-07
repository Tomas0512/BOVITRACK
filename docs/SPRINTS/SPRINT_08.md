# SCRUM - Sprint 8 (Final)
## BoviTrack · Cierre Web — Alertas, Auditoría y QA Final

> **Nota de reprogramación:** Los Sprints 9 y 10 planificados originalmente fueron **absorbidos en este Sprint 8** debido a la fecha límite real del proyecto (23 de agosto de 2026). El enfoque de este sprint es **cerrar el desarrollo web al 100%**: construir las HUs pendientes (HU014, HU015), estabilizar y probar todos los módulos, y preparar la demo final. HU016 (modo offline) queda **fuera de alcance** por ser funcionalidad móvil y la de mayor riesgo (ver sección "Decisiones de alcance").

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 8 (Final) |
| **Duracion** | 16 días calendario |
| **Fecha inicio** | 8 de agosto de 2026 |
| **Fecha fin** | 23 de agosto de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Decisiones de alcance

- **HU016 — Registro sin conexión: FUERA DE ALCANCE (pospuesta).** Es una funcionalidad exclusiva de la app móvil, la más compleja y riesgosa (cola local, versionado, sincronización, resolución de conflictos). Con la fecha límite del 23 de agosto y el foco en cerrar el 100% del desarrollo web, se documenta como pendiente para un futuro. Su Story Points se liberan para QA y estabilización.
- **Cierre del proyecto sin despliegue en producción.** Por ser un proyecto educativo, el "despliegue" se reduce a la **demo funcional en Docker** (local) con datos de prueba representativos. No se configuran servidor, dominio, SSL ni CI/CD en la nube.
- **Bitácora de 20 bugs (AcademyBugs):** no forma parte de este proyecto; es evidencia académica del laboratorio de QA (RAP 593105-05), entregable aparte.

---

## Objetivo del Sprint

> Al finalizar el sprint (23 de agosto), la aplicación web BoviTrack estará **completa y estable**: el usuario podrá configurar y recibir alertas automáticas con historial (HU014), el administrador podrá consultar, filtrar y exportar la auditoría del sistema (HU015), y todos los módulos HU001–HU013 quedarán probados y sin bugs críticos, listos para la demo final con el cliente.

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint8-tomas` |
| Edwin | `feature/sprint8-edwin` |
| Camilo | `feature/sprint8-camilo` |

- **Documentacion (`docs/SPRINTS/`)** se actualiza directo en `main`.
- **Codigo** se trabaja en cada rama. Cada persona trabaja **solo** en sus archivos exclusivos (ver "Mapa de aislamiento").
- **Merge a `main`** al cierre del sprint vía PR. Los únicos puntos de integración compartidos (`fe/src/App.tsx` para rutas, `be/app/main.py` para registro de routers) se resuelven en el PR de merge; no bloquean a nadie durante el desarrollo.

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~40h por persona en el sprint (16 días).

| ID | Historia de Usuario | Prioridad | Story Points | Responsable |
|---|---|---|---|---|
| HU014 | Recibir alertas y notificaciones | Alta | 5 | Tomas |
| HU015 | Revisar auditorías del sistema | Alta | 5 | Camilo |
| QA | Estabilización y cierre web (HU001–HU013) | Alta | 7 | Edwin |

**Total Story Points del Sprint: 17** (~51h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Canales de notificacion definidos (in-app y/o email)
- [x] Auditoria existente revisada: faltan endpoints de filtros y exportacion (solo existe el registro via `audit_service`)
- [x] HU016 fuera de alcance acordada por el equipo (fecha limite 23 de agosto)
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Mapa de aislamiento (independencia entre personas)

Cada persona es dueña completa de su HU o área y **no depende de los demás**. Reglas:

1. **Una HU = una persona** (backend + frontend + QA propio).
2. Cada quien edita **solo** sus archivos exclusivos.
3. Los bugs encontrados en la HU de alguien los corrige el dueño de esa HU.
4. Edwin hace QA de regresión **solo** sobre módulos estables (HU001–HU013), no sobre archivos que Tomas o Camilo están modificando en este sprint.

| Persona | Archivos exclusivos |
|---|---|
| **Tomas (HU014)** | `be/app/routers/alerts.py`, `be/app/schemas/alert*.py` (nuevos), modelos `Notification*` (nuevos) + migración, `be/app/services/notification_service.py` (nuevo), `fe/src/pages/AlertasPage.tsx` (nuevo), `fe/src/api/alerts.ts` |
| **Camilo (HU015)** | `be/app/routers/audit.py` (nuevo), `be/app/services/audit_service.py`, `be/app/schemas/audit*.py` (nuevos), `fe/src/pages/AuditPage.tsx` (nuevo), `fe/src/api/audit_logs.ts`, `fe/src/components/audit/` |
| **Edwin (QA/Cierre)** | Módulos estables HU001–HU013 (backend + frontend), `be/seed_test_data.py`, `docs/`, `docs/BoviTrack.postman_collection.json` |

> **Puntos de integración acotados:** `fe/src/App.tsx` (Tomas y Camilo agregan sus rutas en sus ramas; se integra en el merge) y `be/app/main.py` (Camilo registra `audit` router; se integra en el merge). No constituyen bloqueo.

---

## Sprint Backlog

### HU014 - Alertas y Notificaciones — **Tomas** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 14.1 | Backend: modelo `UserNotificationPref` (canal/frecuencia) + migracion | Tomas | 🔲 Por hacer | 3h |
| 14.2 | Backend: motor de notificaciones por eventos proximos (reusa `alerts.py`) + modelo `NotificationLog` + historial | Tomas | 🔲 Por hacer | 4h |
| 14.3 | Backend: endpoint de preferencias de notificacion (GET/PUT) | Tomas | 🔲 Por hacer | 2h |
| 14.4 | Frontend: pagina web "Alertas" (configuracion de preferencias + historial + AlertBanner) | Tomas | 🔲 Por hacer | 5h |
| 14.5 | Self-QA HU014 + tests | Tomas | 🔲 Por hacer | 2h |

### HU015 - Auditorias del Sistema — **Camilo** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 15.1 | Backend: endpoint `GET /api/v1/admin/audit-logs` con filtros (usuario, accion, entidad, rango de fechas, finca) | Camilo | 🔲 Por hacer | 4h |
| 15.2 | Backend: exportacion filtrada (CSV/Excel) | Camilo | 🔲 Por hacer | 3h |
| 15.3 | Frontend: pagina web "Auditoria" (filtros + tabla + boton descarga) | Camilo | 🔲 Por hacer | 5h |
| 15.4 | Self-QA HU015 + tests | Camilo | 🔲 Por hacer | 2h |

### QA y Cierre Web — **Edwin** (no incluye HU nueva)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 16.1 | QA de regresion modulo auth (HU001) y fincas/potreros (HU002-HU003) | Edwin | 🔲 Por hacer | 4h |
| 16.2 | QA de regresion bovinos y productivo (HU004-HU005) | Edwin | 🔲 Por hacer | 4h |
| 16.3 | QA de regresion reproductivo, terneros y sanitario (HU006-HU008) | Edwin | 🔲 Por hacer | 4h |
| 16.4 | QA de regresion movimientos, economia e inventario (HU009-HU011) | Edwin | 🔲 Por hacer | 4h |
| 16.5 | QA de regresion documentos, reportes y mobile auth (HU012-HU013 + app movil) | Edwin | 🔲 Por hacer | 3h |
| 16.6 | Correccion de bugs en modulos estables (los bugs de HU014/HU015 los corrigen sus duenos) | Edwin | 🔲 Por hacer | 6h |
| 16.7 | Seed de datos demo representativos + prueba de flujo completo end-to-end | Edwin | 🔲 Por hacer | 3h |
| 16.8 | Actualizar Postman collection + documentacion (README / API) | Edwin | 🔲 Por hacer | 3h |
| 16.9 | Preparar evidencias de cierre por modulo | Edwin | 🔲 Por hacer | 2h |

---

## Definition of Done (DoD)

- [ ] Web 100% funcional (HU001–HU015), sin bugs criticos ni altos conocidos
- [ ] HU014: alertas configurables, notificaciones enviadas y registradas en historial
- [ ] HU015: auditoria filtrable por usuario/accion/fecha y exportable
- [ ] QA de regresion HU001–HU013 completado sin bloqueantes
- [ ] Demo final preparada y ejecutada con el cliente (Luis Barbosa) antes del 23 de agosto
- [ ] Documentacion y Postman collection actualizadas
- [ ] Repositorio con tag de version `v1.0.0`
- [ ] HU016 documentada como fuera de alcance

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Bugs criticos heredados que abren modulos ya cerrados | Media | Alto | Priorizar fixes sobre nuevas funcionalidades; Edwin los atiende en paralelo a Tomas/Camilo |
| Colisiones en `App.tsx` / `main.py` al mergear | Media | Bajo | Rutas y routers se integran en el PR de merge; solo 2 archivos compartidos |
| Alcance de HU014/HU015 subestimado | Media | Medio | HU016 fuera de alcance libera capacidad de respaldo |
| Notificaciones duplicadas o perdidas | Media | Alto | Idempotencia y trazabilidad de envios (HU014) |

---

## Sprint Review

**Fecha:** 23 de agosto de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| HU014 — Alertas y notificaciones | 🔲 Pendiente | |
| HU015 — Auditoria filtrable y exportable | 🔲 Pendiente | |
| QA de regresion HU001–HU013 | 🔲 Pendiente | |
| Demo final | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones finales

- Ejecutar demo final con todos los modulos integrados
- Completar retrospectiva final del proyecto
- Cerrar con tag `v1.0.0`
