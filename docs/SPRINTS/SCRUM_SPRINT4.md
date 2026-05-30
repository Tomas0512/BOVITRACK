# SCRUM — Sprint 4
## BoviTrack · Control Productivo, Sanitario, Reproductivo y Comercial

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 4 |
| **Duración** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 16 de mayo de 2026 |
| **Fecha fin** | 29 de mayo de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el usuario autorizado podrá registrar alimentación, ordeños y pesajes con historial por animal, y el veterinario podrá gestionar tratamientos sanitarios individuales.

> ⚠️ **Nota de planificación:** Este sprint fue originalmente estimado en 34 story points (5 HUs), lo que resultó inviable en 2 semanas. El alcance fue redistribuido: HU005 y HU008 quedan en Sprint 4, mientras que HU006, HU007 y HU009 se continuaron en Sprints 5, 6 y 7 respectivamente. Esta redistribución es la práctica correcta de refinamiento de backlog.

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU005 | Como usuario autorizado quiero registrar alimentación, ordeños y pesajes para llevar control productivo del ganado | Alta | 8 |
| HU008 | Como Veterinario quiero planificar y registrar actividades sanitarias para asegurar salud preventiva y correctiva | Alta | 8 |

**Total Story Points del Sprint: 16** *(HU006 → Sprint 5, HU007 → Sprint 6, HU009 → Sprint 7)*

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verificó:

- [x] Criterios de aceptación definidos y validados con el equipo
- [x] Entidades y campos del modelo identificados
- [x] Dependencias con módulos existentes revisadas (Food, MilkProduction, Treatment)
- [x] Endpoints de referencia definidos en colección Postman
- [x] Sin bloqueos técnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU005 — Alimentación, Ordeños y Pesajes

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 5.1 | Revisar modelos existentes (`Food`, `MilkProduction`) y extender si falta campo de peso | Camilo | 🔲 Por hacer | 2h |
| 5.2 | Endpoint `POST /farms/{id}/bovines/{id}/weights` para registrar pesajes con fecha | Camilo | 🔲 Por hacer | 3h |
| 5.3 | Endpoint `GET /farms/{id}/bovines/{id}/weights` para consultar historial de pesos | Edwin | 🔲 Por hacer | 2h |
| 5.4 | Revisar y completar endpoints de alimentación (`/food`) si faltan filtros por bovino | Tomas | 🔲 Por hacer | 2h |
| 5.5 | Revisar y completar endpoints de producción de leche (`/milk-production`) | Edwin | 🔲 Por hacer | 2h |
| 5.6 | Componente `WeightHistory` con tabla de pesajes por animal | Tomas | 🔲 Por hacer | 3h |
| 5.7 | Componente `MilkProductionList` con registros diarios de ordeño | Tomas | 🔲 Por hacer | 3h |
| 5.8 | Componente `FoodList` con registros de alimentación por animal o lote | Edwin | 🔲 Por hacer | 3h |
| 5.9 | Gráfico de evolución de peso con línea de tiempo (Chart.js o Recharts) | Camilo | 🔲 Por hacer | 5h |
| 5.10 | Integrar los tres componentes en `BovineDetailPage` con pestañas | Tomas | 🔲 Por hacer | 3h |

### HU008 — Actividades Sanitarias *(movido desde posición 4)*

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 8.1 | Revisar modelo `Treatment` existente y validar que cubre tratamientos y enfermedades | Camilo | 🔲 Por hacer | 1h |
| 8.2 | Modelo ORM `SanitaryPlan` (nombre, tipo, fecha inicio, frecuencia, próxima fecha) | Edwin | 🔲 Por hacer | 3h |
| 8.3 | Migración Alembic para tabla `sanitary_plan` | Camilo | 🔲 Por hacer | 1h |
| 8.4 | Schema + service + CRUD para planes sanitarios (`/farms/{id}/sanitary-plans`) | Edwin | 🔲 Por hacer | 4h |
| 8.5 | Lógica de cálculo de próxima fecha según frecuencia (diaria, semanal, mensual, anual) | Camilo | 🔲 Por hacer | 3h |
| 8.6 | Endpoint de alertas: eventos sanitarios en los próximos 7 días (`/farms/{id}/alerts`) | Camilo | 🔲 Por hacer | 3h |
| 8.7 | Componente `SanitaryPlanList` con tabla y badge de próxima fecha | Tomas | 🔲 Por hacer | 3h |
| 8.8 | Componente `AlertBanner` en `FarmDetailPage` mostrando alertas activas | Edwin | 🔲 Por hacer | 2h |
| 8.9 | Integrar tratamientos existentes (`TreatmentList`) en pestaña "Sanidad" de `BovineDetailPage` | Tomas | 🔲 Por hacer | 2h |

---

## Definition of Done (DoD)

Un ítem se considera **Hecho** cuando cumple todos los criterios:

- [ ] El endpoint backend responde correctamente (200/201/204 según corresponda)
- [ ] Las validaciones Pydantic rechazan datos inválidos (422 con detalle)
- [ ] El componente frontend muestra y actualiza datos sin recargar la página
- [ ] Los permisos RBAC están aplicados en el endpoint correspondiente
- [ ] La migración Alembic corre sin errores (`alembic upgrade head`)
- [ ] No hay errores de TypeScript en el frontend
- [ ] No hay errores de importación en Python
- [ ] El componente está integrado en la página correspondiente (no "huérfano")

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| HU006 (parto → ternero automático) tiene lógica compleja | Media | Alto | Desarrollar primero sin automatismo, luego agregar |
| HU008 requiere dos modelos nuevos (plan + alerta) | Media | Medio | Empezar por alertas simples sin planes complejos |
| Recharts / Chart.js puede requerir configuración extensa | Baja | Medio | Usar una librería ya evaluada desde el inicio |
| El módulo de alimentación ya existe parcialmente — riesgo de duplicar lógica | Media | Medio | Revisar el backend existente antes de crear nuevo código |

---

## Orden de implementación sugerido

```
Semana 1: HU005 — backend (pesajes, filtros food/milk) + vertical slice: endpoint + componente WeightHistory
Semana 2: HU008 — Treatment review + SanitaryPlan + AlertBanner integrado en FarmDetailPage
```

---

## Backlog para Sprints futuros (referencia)

| ID | Historia | Sprint sugerido |
|---|---|---|
| HU006 | Control reproductivo (servicios, partos, fecha estimada) | Sprint 5 |
| HU007 | Desarrollo y seguimiento de terneros | Sprint 6 |
| HU009 | Ingresos y salidas de animales | Sprint 7 |
| HU010 | Información económica e indicadores de rentabilidad | Sprint 7 |
| HU011 | Inventarios y compras de insumos | Sprint 8 |
| HU012 | Subir y gestionar documentos | Sprint 8 |
| HU013 | Reportes e indicadores de desempeño | Sprint 9 |
| HU014 | Alertas y notificaciones automáticas | Sprint 9 |
| HU015 | Revisión de auditorías del sistema | Sprint 10 |
| HU016 | Registro de datos sin conexión (offline) | Sprint 10 |
