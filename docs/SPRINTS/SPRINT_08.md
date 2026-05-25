# SCRUM - Sprint 8
## BoviTrack · Inventario Completo y Gestion Documental

---

## Informacion General

| Campo | Valor |
|---|---|
| **Proyecto** | BoviTrack |
| **Sprint** | Sprint 8 |
| **Duracion** | 15 dias |
| **Fecha inicio** | 11 de julio de 2026 |
| **Fecha fin** | 24 de julio de 2026 |
| **Equipo** | Camilo Ortiz, Tomas Canon, Edwin Delgado |
| **Roles Scrum** | Camilo Ortiz (Developer / Scrum Master), Tomas Canon (Developer / Product Owner), Edwin Delgado (Developer) |

---

## Objetivo del Sprint

> Cerrar HU011 (inventarios/compras de insumos) e implementar HU012 para carga, vinculacion y descarga de documentos.

---

## Product Backlog seleccionado para este Sprint

| ID | Historia de Usuario | Prioridad | Story Points |
|---|---|---|---|
| HU011 (cierre) | Gestionar inventarios y compras de insumos | Alta | 8 |
| HU012 | Subir y gestionar documentos | Media | 5 |

**Total Story Points del Sprint: 13**

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

**Fecha:** 16 de julio de 2026  
**Participantes:** Camilo Ortiz, Tomas Canon, Edwin Delgado

### Incremento entregado

Pendiente de ejecucion.

---

## Sprint Retrospectiva

### Que salio bien?

Pendiente.

### Que se puede mejorar?

Pendiente.
