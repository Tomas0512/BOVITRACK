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
| **Fecha de cierre real** | 1 de junio de 2026 |
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

| # | Tarea | Responsable | Estado | Estimación | Notas |
|---|---|---|---|---|---|
| 5.1 | Crear modelo ORM `Weight` con campos `weight_kg`, `measured_at`, `daily_gain`, `body_condition` | Tomas | ✅ Hecho | 2h | `be/app/models/weight.py` |
| 5.2 | Endpoint `POST /farms/{id}/weights` — registrar pesaje con cálculo automático de ganancia diaria | Tomas | ✅ Hecho | 3h | `be/app/routers/weights.py` |
| 5.3 | Endpoint `GET /farms/{id}/weights?bovine_id=` — historial de pesos filtrado por bovino | Tomas | ✅ Hecho | 2h | `be/app/services/weight_service.py` |
| 5.4 | Revisar y completar endpoints de alimentación (`/food`) con filtro por bovino | Tomas | ✅ Hecho | 2h | Endpoints existentes validados |
| 5.5 | Revisar y completar endpoints de producción de leche (`/milk-production`) | Tomas | ✅ Hecho | 2h | Endpoints existentes validados |
| 5.6 | Componente `WeightHistory` con tabla de pesajes y formulario de registro inline | Tomas | ✅ Hecho | 3h | `fe/src/components/bovines/WeightHistory.tsx` |
| 5.7 | Componente `MilkProductionList` con registros diarios de ordeño | Tomas | ✅ Hecho | 3h | `fe/src/components/bovines/MilkProductionList.tsx` |
| 5.8 | Componente `FoodList` con registros de alimentación por animal | Tomas | ✅ Hecho | 3h | `fe/src/components/bovines/FoodList.tsx` |
| 5.9 | Gráfico de evolución de peso con línea de tiempo (Recharts) | Tomas | ✅ Hecho | 5h | `fe/src/components/bovines/WeightChart.tsx` |
| 5.10 | Integrar los tres componentes en `BovineDetailPage` con pestañas (General / Productivo / Sanitario) | Tomas | ✅ Hecho | 3h | `fe/src/pages/BovineDetailPage.tsx` |

### HU008 — Actividades Sanitarias

| # | Tarea | Responsable | Estado | Estimación | Notas |
|---|---|---|---|---|---|
| 8.1 | Revisar modelo `Treatment` existente y validar que cubre tratamientos y enfermedades | Tomas | ✅ Hecho | 1h | Modelo validado, sin cambios necesarios |
| 8.2 | Modelo ORM `SanitaryPlan` (nombre, tipo, fecha inicio, frecuencia, próxima fecha) | Edwin | 🔲 Pendiente | 3h | Movido a Sprint 5 si Edwin no lo completa |
| 8.3 | Migración Alembic para tabla `sanitary_plan` | Camilo | 🔲 Pendiente | 1h | Depende de 8.2 |
| 8.4 | Schema + service + CRUD para planes sanitarios (`/farms/{id}/sanitary-plans`) | Edwin | 🔲 Pendiente | 4h | Depende de 8.2 |
| 8.5 | Lógica de cálculo de próxima fecha según frecuencia (diaria, semanal, mensual, anual) | Camilo | 🔲 Pendiente | 3h | Depende de 8.2 |
| 8.6 | Endpoint de alertas: eventos sanitarios en los próximos 7 días (`/farms/{id}/alerts`) | Camilo | 🔲 Pendiente | 3h | Depende de 8.4 |
| 8.7 | Componente `SanitaryPlanList` con tabla y badge de próxima fecha | Tomas | 🔲 Pendiente | 3h | Depende de 8.4 |
| 8.8 | Componente `AlertBanner` en `FarmDetailPage` mostrando alertas activas | Edwin | 🔲 Pendiente | 2h | Depende de 8.6 |
| 8.9 | Integrar `TreatmentList` en pestaña "Sanitario" de `BovineDetailPage` | Tomas | ✅ Hecho | 2h | `fe/src/components/bovines/TreatmentList.tsx` |

### Infraestructura y Base de Datos *(tareas emergentes del sprint)*

| # | Tarea | Responsable | Estado | Estimación | Notas |
|---|---|---|---|---|---|
| I.1 | Migración Alembic inicial (`c9ff44fd3509`) — creación de todas las tablas | Tomas | ✅ Hecho | 2h | `be/alembic/versions/c9ff44fd3509_initial_schema.py` |
| I.2 | Seed de 33 departamentos y 150 municipios de Colombia | Tomas | ✅ Hecho | 1h | `be/seed_departments.py` |
| I.3 | Seed de 7 propósitos de finca | Tomas | ✅ Hecho | 1h | `be/seed_purposes.py` |
| I.4 | Seed de roles (Administrador, Operario, Veterinario, Auditor) con 36 permisos RBAC | Tomas | ✅ Hecho | 2h | `be/seed_roles.py` |
| I.5 | Corrección de asignación automática de rol al crear finca (`UserFarm`) | Tomas | ✅ Hecho | 1h | Fix en `seed_roles.py` + `farm_service.py` |

---

## Definition of Done (DoD)

| Criterio | HU005 | HU008 (parcial) |
|---|---|---|
| Endpoints responden 200/201/204 según corresponda | ✅ | ✅ (Treatment) / 🔲 (SanitaryPlan) |
| Validaciones Pydantic rechazan datos inválidos (422) | ✅ | ✅ (Treatment) / 🔲 (SanitaryPlan) |
| Componentes frontend muestran y actualizan datos sin recargar | ✅ | ✅ (TreatmentList) / 🔲 (AlertBanner, SanitaryPlanList) |
| Permisos RBAC aplicados en endpoints | ✅ | ✅ (Treatment) / 🔲 (SanitaryPlan) |
| Migración Alembic corre sin errores | ✅ | ✅ |
| Sin errores de TypeScript en frontend | ✅ | ✅ |
| Sin errores de importación en Python | ✅ | ✅ |
| Componentes integrados en página correspondiente | ✅ | ✅ (TreatmentList) / 🔲 (AlertBanner) |

---

## Retrospectiva del Sprint

### ¿Qué salió bien?
- HU005 completada al 100%: modelos, endpoints, servicios y todos los componentes frontend
- Se implementó cálculo automático de ganancia diaria de peso (valor agregado)
- Infraestructura de BD completamente funcional con seeds y migración inicial
- Ambiente Docker funcional con los 3 servicios (DB, BE, FE)

### ¿Qué salió mal?
- Las tareas 8.2–8.8 de HU008 (`SanitaryPlan`) no fueron completadas por el responsable asignado
- Surgieron tareas de infraestructura no planificadas (migrations, seeds, RBAC fix) que consumieron ~7h adicionales

### Velocidad real del sprint

| Métrica | Valor |
|---|---|
| Story Points planificados | 16 |
| Story Points completados | 8 (HU005) |
| Story Points pendientes | 8 (HU008 parcial) |
| Tareas emergentes resueltas | 5 (infraestructura) |

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| HU006 (parto → ternero automático) tiene lógica compleja | Media | Alto | Desarrollar primero sin automatismo, luego agregar |
| HU008 requiere dos modelos nuevos (plan + alerta) | Media | Medio | Empezar por alertas simples sin planes complejos |
| Recharts / Chart.js puede requerir configuración extensa | Baja | Medio | ✅ Resuelto: Recharts funcionó correctamente |
| El módulo de alimentación ya existe parcialmente — riesgo de duplicar lógica | Media | Medio | ✅ Resuelto: endpoints existentes fueron reutilizados |

---

## Backlog para Sprints futuros (referencia)

| ID | Historia | Sprint sugerido | Estado |
|---|---|---|---|
| HU008 (8.2–8.8) | SanitaryPlan + AlertBanner (pendiente Edwin/Camilo) | Sprint 5 | 🔲 Pendiente |
| HU006 | Control reproductivo (servicios, partos, fecha estimada) | Sprint 5 | 🔲 Pendiente |
| HU007 | Desarrollo y seguimiento de terneros | Sprint 6 | 🔲 Pendiente |
| HU009 | Ingresos y salidas de animales | Sprint 7 | 🔲 Pendiente |
| HU010 | Información económica e indicadores de rentabilidad | Sprint 7 | 🔲 Pendiente |
| HU011 | Inventarios y compras de insumos | Sprint 8 | 🔲 Pendiente |
| HU012 | Subir y gestionar documentos | Sprint 8 | 🔲 Pendiente |
| HU013 | Reportes e indicadores de desempeño | Sprint 9 | 🔲 Pendiente |
| HU014 | Alertas y notificaciones automáticas | Sprint 9 | 🔲 Pendiente |
| HU015 | Revisión de auditorías del sistema | Sprint 10 | 🔲 Pendiente |
| HU016 | Registro de datos sin conexión (offline) | Sprint 10 | 🔲 Pendiente |