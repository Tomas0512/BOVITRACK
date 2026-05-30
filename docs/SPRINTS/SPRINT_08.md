# SCRUM - Sprint 8
## BoviTrack · Inventario Completo y Gestion Documental

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 8 |
| **Duracion** | 2 semanas (14 días calendario) |
| **Fecha inicio** | 11 de julio de 2026 |
| **Fecha fin** | 24 de julio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Al final del sprint, el administrador podra gestionar el inventario de insumos con control de stock y alertas de minimo (HU011), y subir, consultar y descargar documentos vinculados a fincas, bovinos o eventos (HU012).

---

## Product Backlog seleccionado para este Sprint

> **Equivalencia del equipo:** 1 Story Point ≈ 3 horas de trabajo efectivo. Capacidad del equipo: ~60h por sprint (3 personas × ~20h disponibles).

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU011 (cierre) | Gestionar inventarios y compras de insumos | Alta | 8 |
| HU012 | Subir y gestionar documentos | Media | 5 |

**Total Story Points del Sprint: 13** (~39h estimadas, dentro de la capacidad del equipo)

---

## Definition of Ready (DoR)

Antes de iniciar una HU en este sprint se verifica:

- [x] Criterios de aceptacion definidos y acordados con el equipo
- [x] Estrategia de almacenamiento de archivos definida (filesystem local vs S3)
- [x] Tipos y tamanos maximos de archivos permitidos acordados
- [x] Dependencia de inventario con consumos de `Food` revisada
- [x] Sin bloqueos tecnicos conocidos al inicio del sprint

---

## Sprint Backlog

### HU011 - Inventarios y Compras de Insumos (cierre)

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 11.1 | Completar flujo de compras con impacto en stock y costo | Camilo | 🔲 Por hacer | 4h |
| 11.2 | Trazabilidad de entradas/salidas por modulo origen | Edwin | 🔲 Por hacer | 3h |
| 11.3 | Ajustes de alertas de stock minimo | Camilo | 🔲 Por hacer | 2h |
| 11.4 | Pantalla de inventario y compras | Tomas | 🔲 Por hacer | 4h |

### HU012 - Gestion de Documentos

| # | Tarea | Responsable | Estado | Estimacion |
|---|---|---|---|---|
| 12.1 | Modelo `Document` + almacenamiento y metadata | Edwin | 🔲 Por hacer | 4h |
| 12.2 | Endpoints upload/list/download/delete | Camilo | 🔲 Por hacer | 4h |
| 12.3 | Asociacion a finca, bovino o evento | Edwin | 🔲 Por hacer | 3h |
| 12.4 | UI de carga y repositorio documental | Tomas | 🔲 Por hacer | 5h |
| 12.5 | QA funcional HU011/HU012 | Edwin | 🔲 Por hacer | 3h |

---

## Definition of Done (DoD)

- [ ] Stock se actualiza automaticamente por compras/consumos
- [ ] Documentos suben, se listan y se descargan correctamente
- [ ] Asociaciones a entidades del sistema funcionales
- [ ] Sin errores de seguridad evidentes en archivos
- [ ] Evidencia funcional y pruebas minimas

---

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Manejo inseguro de archivos subidos | Media | Alto | Validar tipo/tamano y sanitizar nombres |
| Descuadre entre costo y stock | Media | Medio | Validar transacciones de compra/consumo |

---

## Sprint Review

**Fecha:** 24 de julio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

| Modulo | Entregado | Observaciones |
|---|---|---|
| Stock actualizado por compras/consumos | 🔲 Pendiente | |
| Alertas de stock minimo funcionales | 🔲 Pendiente | |
| UI de inventario y compras | 🔲 Pendiente | |
| Upload/download/delete de documentos | 🔲 Pendiente | |
| Asociacion documental a finca/bovino/evento | 🔲 Pendiente | |

### Story Points completados

Pendiente de cierre.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente de completar al cierre del sprint.

### Que se puede mejorar?

Pendiente de completar al cierre del sprint.

### Acciones para Sprint 9

- Verificar que los modulos de HU011 y HU012 exponen datos consumibles por los reportes de HU013.
- Validar seguridad en manejo de archivos antes de avanzar (OWASP: file upload).
