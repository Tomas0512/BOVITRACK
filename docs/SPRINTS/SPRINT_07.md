# SCRUM - Sprint 7
## BoviTrack · Reportes, Inventarios y Gestion Documental

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 7 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 27 de junio de 2026 |
| **Fecha fin** | 10 de julio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Flujo de trabajo por ramas

| Persona | Rama |
|---------|------|
| Tomas | `feature/sprint7-tomas` |
| Edwin | `feature/sprint7-edwin` |
| Camilo | `feature/sprint7-camilo` |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra generar y exportar reportes productivos, sanitarios y economicos con filtros por fecha (HU013 cierre), gestionar el inventario de insumos con control de stock y alertas de minimo (HU011 cierre), y subir, consultar y descargar documentos vinculados a fincas, bovinos o eventos (HU012).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU013 (cierre) | Generar reportes e indicadores | Alta | 8 |
| HU011 (cierre) | Gestionar inventarios y compras de insumos | Alta | 8 |
| HU012 | Subir y gestionar documentos | Media | 5 |

**Total Story Points del Sprint: 21** (~63h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar las HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Formatos de exportacion acordados (PDF y/o Excel)
- [x] Fuentes de datos de reportes identificadas (modulos HU005-HU012)
- [x] Estrategia de almacenamiento de archivos definida (filesystem local vs S3)
- [x] Tipos y tamanos maximos de archivos permitidos acordados
- [x] Dependencia de inventario con consumos de `Food` revisada
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU013 - Reportes e Indicadores (cierre) — **Tomas** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 13.1 | Completar filtros de reportes por fecha/categoria | Tomas | ✅ Hecho | 3h |
| 13.2 | Exportacion PDF/Excel | Tomas | ✅ Hecho | 4h |
| 13.3 | Pantalla de reportes con descarga | Tomas | ✅ Hecho | 4h |
| 13.4 | Ajustes de indicadores productivos/sanitarios/economicos | Tomas | ✅ Hecho | 3h |

### HU011 - Inventarios y Compras de Insumos (cierre) — **Edwin** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 11.1 | Completar flujo de compras con impacto en stock y costo | Edwin | ✅ Hecho | 4h |
| 11.2 | Trazabilidad de entradas/salidas por modulo origen | Edwin | ✅ Hecho | 3h |
| 11.3 | Ajustes de alertas de stock minimo | Edwin | ✅ Hecho | 2h |
| 11.4 | Pantalla de inventario y compras | Edwin | ✅ Hecho | 4h |

### HU012 - Gestion de Documentos — **Camilo** (asignacion vertical)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 12.1 | Modelo `Document` + almacenamiento y metadata | Camilo | ✅ Hecho | 4h |
| 12.2 | Endpoints upload/list/download/delete | Camilo | ✅ Hecho | 4h |
| 12.3 | Asociacion a finca, bovino o evento | Camilo | ✅ Hecho | 3h |
| 12.4 | UI de carga y repositorio documental | Camilo | ✅ Hecho | 5h |
| 12.5 | QA funcional HU011/HU012/HU013 | Camilo | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

- [x] Reportes exportables en formatos solicitados (HU013 — Tomas)
- [x] Indicadores visibles y con filtros funcionales (HU013 — Tomas)
- [x] Stock se actualiza automaticamente por compras/consumos (HU011 — Edwin)
- [x] Alertas de stock minimo funcionales (HU011 — Edwin)
- [x] Documentos suben, se listan y se descargan correctamente (HU012 — Camilo)
- [x] Asociaciones a entidades del sistema funcionales (HU012 — Camilo)
- [x] Sin errores de seguridad evidentes en archivos
- [x] Sin errores tecnicos en backend/frontend
- [x] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Fallas en generacion de archivos grandes (PDF/Excel) | Media | Medio | Limitar rangos y paginar resultados |
| Manejo inseguro de archivos subidos | Media | Alto | Validar tipo/tamano y sanitizar nombres |
| Descuadre entre costo y stock | Media | Medio | Validar transacciones de compra/consumo |

---

## Sprint Review

**Fecha:** 10 de julio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Reportes con filtros por fecha/categoria | ✅ Entregado | HU013 — Tomas |
| Exportacion PDF/Excel funcional | ✅ Entregado | HU013 — Tomas |
| Indicadores productivos/sanitarios/economicos | ✅ Entregado | HU013 — Tomas |
| Stock actualizado por compras/consumos | 🔲 Pendiente | HU011 — Edwin |
| Alertas de stock minimo funcionales | 🔲 Pendiente | HU011 — Edwin |
| UI de inventario y compras | 🔲 Pendiente | HU011 — Edwin |
| Upload/download/delete de documentos | ✅ Entregado | HU012 — Camilo |
| Asociacion documental a finca/bovino/evento | ✅ Entregado | HU012 — Camilo |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 8

- Verificar que los modulos de reportes exponen datos consumibles por HU015 (auditoria)
- Validar seguridad en manejo de archivos antes de avanzar (OWASP: file upload)
- Revisar velocidad real del equipo vs 21 puntos planificados
