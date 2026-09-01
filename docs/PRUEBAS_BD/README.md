# Pruebas de Base de Datos — BoviTrack (Guía 6)

> Evidencia de las pruebas de base de datos solicitadas en la Guía 6 del
> entregable. Incluye la matriz BD vs. aplicación y el script SQL de verificación.

## Contenido

| Archivo | Descripción |
|---|---|
| `01_Matriz_BD_vs_Aplicacion.pdf` | Matriz que cruza cada tabla/punto de la BD con el módulo de la aplicación (evidencia de cobertura). |
| `02_Pruebas_BD_BoviTrack.sql` | Script SQL de los casos de prueba **CP01–CP27** (con acción de la API, resultado esperado, resultado obtenido y consulta de verificación). |

## Nota sobre los resultados (OBTENIDO)
Los valores `HTTP` y de BD anotados en `02_Pruebas_BD_BoviTrack.sql` corresponden
a la fecha de generación original (27/8/2026). Varios casos que figuraban como
`HTTP 500` o con descuadre ya fueron corregidos en el proyecto (rama
`fix/auditoria-seguridad`), por ejemplo:

- **CP13** (identificación duplicada de bovino) → ahora `HTTP 409` (antes 500).
- **CP14** (bovino con lote inexistente) → ahora `HTTP 400` (antes 500).
- **CP20** (eliminar bovino) → borrado lógico correcto (`is_active=f`).
- **CP25** (nombre de alimento > 255) → ahora `HTTP 422` (antes 500).
- **CP26** (inventario vs. kárdex) → el consumo ahora registra un
  `stock_movement` de tipo `consumption`, manteniendo coherencia
  `stock_after - stock_before = quantity`.

Para regenerar la evidencia contra el estado actual de la base y la API, ejecutar
los pasos del propio script `02_Pruebas_BD_BoviTrack.sql` y anotar los nuevos
resultados.
