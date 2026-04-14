# SCRUM — Sprint 4
## BoviTrack · Control Productivo, Sanitario, Reproductivo y Comercial

---

## Información General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 4 |
| **Duración** | 4 semanas |
| **Fecha inicio** | 20 de abril de 2026 |
| **Fecha fin** | 17 de mayo de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Cañon |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Cañon (Developer / Product Owner) |

---

## Objetivo del Sprint

> Extender el sistema con los módulos productivos y sanitarios del hato: registro de alimentación, ordeños y pesajes con gráficos de evolución; control reproductivo y seguimiento de terneros; planificación de actividades sanitarias con alertas; y registro de movimientos comerciales de animales (compras, ventas, traslados). Al final del sprint el ganadero podrá gestionar el ciclo completo de producción y salud de su hato.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU005 | Como usuario autorizado quiero registrar alimentación, ordeños y pesajes para llevar control productivo del ganado | Alta | 8 |
| HU006 | Como Veterinario quiero registrar control reproductivo para dar seguimiento a servicios, diagnósticos y partos | Alta | 8 |
| HU007 | Como Capataz quiero registrar el desarrollo de los terneros para monitorear su crecimiento y salud | Media | 5 |
| HU008 | Como Veterinario quiero planificar y registrar actividades sanitarias para asegurar salud preventiva y correctiva | Alta | 8 |
| HU009 | Como Administrador quiero registrar ingresos y salidas de animales para llevar control comercial y físico del hato | Alta | 5 |

**Total Story Points del Sprint: 34**

---

## Sprint Backlog

### HU005 — Alimentación, Ordeños y Pesajes

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 5.1 | Revisar modelos existentes (`Food`, `MilkProduction`) y extender si falta campo de peso | Camilo | 🔲 Por hacer | 2h |
| 5.2 | Endpoint `POST /farms/{id}/bovines/{id}/weights` para registrar pesajes con fecha | Camilo | 🔲 Por hacer | 3h |
| 5.3 | Endpoint `GET /farms/{id}/bovines/{id}/weights` para consultar historial de pesos | Camilo | 🔲 Por hacer | 2h |
| 5.4 | Revisar y completar endpoints de alimentación (`/food`) si faltan filtros por bovino | Tomas | 🔲 Por hacer | 2h |
| 5.5 | Revisar y completar endpoints de producción de leche (`/milk-production`) | Tomas | 🔲 Por hacer | 2h |
| 5.6 | Componente `WeightHistory` con tabla de pesajes por animal | Tomas | 🔲 Por hacer | 3h |
| 5.7 | Componente `MilkProductionList` con registros diarios de ordeño | Tomas | 🔲 Por hacer | 3h |
| 5.8 | Componente `FoodList` con registros de alimentación por animal o lote | Tomas | 🔲 Por hacer | 3h |
| 5.9 | Gráfico de evolución de peso con línea de tiempo (Chart.js o Recharts) | Camilo | 🔲 Por hacer | 5h |
| 5.10 | Integrar los tres componentes en `BovineDetailPage` con pestañas | Tomas | 🔲 Por hacer | 3h |

### HU006 — Control Reproductivo

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 6.1 | Modelo ORM `ReproductiveEvent` (servicio, diagnóstico, parto, tipo, fecha, resultado) | Camilo | 🔲 Por hacer | 3h |
| 6.2 | Migración Alembic para tabla `reproductive_event` | Camilo | 🔲 Por hacer | 1h |
| 6.3 | Schema Pydantic + service para eventos reproductivos | Camilo | 🔲 Por hacer | 3h |
| 6.4 | CRUD de eventos reproductivos (`/farms/{id}/bovines/{id}/reproductive-events`) | Camilo | 🔲 Por hacer | 3h |
| 6.5 | Cálculo de fecha estimada de parto (+ 283 días desde servicio positivo) | Camilo | 🔲 Por hacer | 2h |
| 6.6 | Al registrar parto: crear automáticamente ficha de ternero (`Bovine` con padres) | Camilo | 🔲 Por hacer | 4h |
| 6.7 | Componente `ReproductiveTimeline` con historial cronológico | Tomas | 🔲 Por hacer | 4h |
| 6.8 | Integrar en `BovineDetailPage` en pestaña "Reproducción" | Tomas | 🔲 Por hacer | 2h |

### HU007 — Desarrollo de Terneros

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 7.1 | Vista filtrada de bovinos con `birth_date` reciente (≤ 6 meses) como sección "Terneros" | Camilo | 🔲 Por hacer | 2h |
| 7.2 | Componente `CalfList` mostrando peso actual, alimentación y estado de terneros | Tomas | 🔲 Por hacer | 3h |
| 7.3 | Gráfico de curva de crecimiento del ternero (peso vs fecha) | Tomas | 🔲 Por hacer | 3h |
| 7.4 | La ficha de ternero reutiliza `BovineDetailPage` con sección de registros de desarrollo | Tomas | 🔲 Por hacer | 2h |

### HU008 — Actividades Sanitarias

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 8.1 | Revisar modelo `Treatment` existente y validar que cubre tratamientos y enfermedades | Camilo | 🔲 Por hacer | 1h |
| 8.2 | Modelo ORM `SanitaryPlan` (nombre, tipo, fecha inicio, frecuencia, próxima fecha) | Camilo | 🔲 Por hacer | 3h |
| 8.3 | Migración Alembic para tabla `sanitary_plan` | Camilo | 🔲 Por hacer | 1h |
| 8.4 | Schema + service + CRUD para planes sanitarios (`/farms/{id}/sanitary-plans`) | Camilo | 🔲 Por hacer | 4h |
| 8.5 | Lógica de cálculo de próxima fecha según frecuencia (diaria, semanal, mensual, anual) | Camilo | 🔲 Por hacer | 3h |
| 8.6 | Endpoint de alertas: eventos sanitarios en los próximos 7 días (`/farms/{id}/alerts`) | Camilo | 🔲 Por hacer | 3h |
| 8.7 | Componente `SanitaryPlanList` con tabla y badge de próxima fecha | Tomas | 🔲 Por hacer | 3h |
| 8.8 | Componente `AlertBanner` en `FarmDetailPage` mostrando alertas activas | Tomas | 🔲 Por hacer | 2h |
| 8.9 | Integrar tratamientos existentes (`TreatmentList`) en pestaña "Sanidad" de `BovineDetailPage` | Tomas | 🔲 Por hacer | 2h |

### HU009 — Ingresos y Salidas de Animales

| # | Tarea | Responsable | Estado | Estimación |
|---|---|---|---|---|
| 9.1 | Modelo ORM `AnimalMovement` (tipo: compra/venta/traslado/pérdida, fecha, precio, entidad) | Camilo | 🔲 Por hacer | 3h |
| 9.2 | Migración Alembic para tabla `animal_movement` | Camilo | 🔲 Por hacer | 1h |
| 9.3 | Schema + service + CRUD para movimientos (`/farms/{id}/animal-movements`) | Camilo | 🔲 Por hacer | 4h |
| 9.4 | Al registrar salida: actualizar `Bovine.status` a "vendido" / "trasladado" / "muerto" | Camilo | 🔲 Por hacer | 2h |
| 9.5 | Al registrar compra: crear `Bovine` con `entry_type = "compra"` y datos del proveedor | Camilo | 🔲 Por hacer | 3h |
| 9.6 | Componente `AnimalMovementList` con historial de movimientos por finca | Tomas | 🔲 Por hacer | 3h |
| 9.7 | Formulario de registro de venta/traslado accesible desde `BovineDetailPage` | Tomas | 🔲 Por hacer | 3h |

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
Semana 1: HU005 (alimentación, ordeños) + HU009 (movimientos backend)
Semana 2: HU006 (reproductivo backend + frontend básico)
Semana 3: HU008 (sanitario + alertas) + HU007 (terneros)
Semana 4: Gráficos, integración en BovineDetailPage, pruebas y ajustes
```

---

## Backlog para Sprints futuros (referencia)

| ID | Historia | Sprint sugerido |
|---|---|---|
| HU010 | Información económica e indicadores de rentabilidad | Sprint 5 |
| HU011 | Inventarios y compras de insumos | Sprint 5 |
| HU012 | Subir y gestionar documentos | Sprint 5 |
| HU013 | Reportes e indicadores de desempeño | Sprint 6 |
| HU014 | Alertas y notificaciones automáticas | Sprint 6 |
| HU015 | Revisión de auditorías del sistema | Sprint 6 |
| HU016 | Registro de datos sin conexión (offline) | Sprint 7 |
