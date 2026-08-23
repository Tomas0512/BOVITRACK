# QA de Cierre — Sprint 8 (Web)

**Responsable:** Edwin Delgado
**Fecha de cierre:** 23 de agosto de 2026
**Alcance:** Regresión completa de los módulos estables **HU001–HU013**, corrección
de bugs, seed de datos demo, suite E2E automatizada y evidencias de cierre
(tareas 16.1 – 16.9).

> Los bugs funcionales de HU014 (Alertas) y HU015 (Auditoría) NO hacen parte de
> este cierre: corresponden a sus dueños (Tomás y Camilo) según el acuerdo del
> equipo. Este documento cubre únicamente lo asignado a Edwin.

---

## 1. Resumen de resultados

| Suite | Resultado | Comando |
|---|---|---|
| Backend (pytest) | ✅ **39/39** | `cd be && .venv/Scripts/python -m pytest tests -q` |
| Frontend E2E (Selenium) | ✅ **30/30** | `cd qa_e2e && .venv/Scripts/python run_all_tests.py` |
| Lint backend (ruff) | ✅ sin hallazgos | `cd be && .venv/Scripts/ruff check app/` |

- Evidencia gráfica: **30 capturas** en `qa_e2e/screenshots/`
  (una por caso de uso, sufijo `_OK_<fecha>.png`).
- Colección Postman actualizada: `docs/BoviTrack.postman_collection.json`
  (carpetas nuevas: Auditoría HU015 y Alertas/Notificaciones HU014).

---

## 2. Cobertura de regresión por módulo (16.1 – 16.5)

| Módulo(s) | HUs | Verificación principal | Resultado |
|---|---|---|---|
| Auth (login/recuperación/reactivación) | HU001 | Credenciales válidas/inválidas, validación required, política de contraseñas | ✅ |
| Fincas y potreros | HU002–HU003 | Wizard valida pasos antes de avanzar; detalle carga pestañas General/Sanitario | ✅ |
| Bovinos y productivo | HU004–HU005 | Detalle de bovino, pesos y producción láctea vía API | ✅ |
| Reproductivo, terneros, sanitario | HU006–HU008 | Eventos respetan `due_date`; planes sanitarios por pestaña | ✅ |
| Movimientos y economía | HU009–HU010 | Dashboard económico renderiza Ingresos/Egresos/**Balance mensual** con datos del seed | ✅ |
| Empleados/usuarios de finca | HU011 | Endpoints protegidos por permisos de rol (Postman) | ✅ |
| Documentos y reportes | HU012–HU013 | Reportes genera reporte con opciones de descarga PDF/Excel | ✅ |
| Mobile auth | — | Reutiliza `/auth/*` validados arriba | ✅ |

---

## 3. Bugs encontrados y corregidos (16.6)

| # | Severidad | Módulo | Bug | Corrección |
|---|---|---|---|---|
| 1 | 🔴 Crítico | Economía/Inventario | `GET /farms/{id}/economics/indicators` devolvía **403 para todos los roles**: el seed definía módulos que no coinciden con los routers (`alimentacion`≠`alimentos`, `planes_sanitarios`≠`sanitario`) y omitía `economica` y `tareas` | `be/seed_roles.py`: matriz alineada a las claves reales de `require_permission()`; seed **auto-correctivo** (upsert en cada ejecución) |
| 2 | 🟠 Alto | Auth (FE) | Olvido de contraseña permitía enviar el formulario vacío | `ForgotPasswordPage.tsx`: atributo `required` en el input email |
| 3 | 🟠 Alto | Auth (FE) | Reset de contraseña habilitaba submit con contraseñas débiles o no coincidentes | `ResetPasswordPage.tsx`: submit deshabilitado hasta cumplir política y coincidencia |
| 4 | 🟠 Alto | Fincas (FE) | Wizard de finca avanzaba de paso con campos obligatorios vacíos | `CreateFarmPage.tsx`: botón "Siguiente" deshabilitado hasta validar el paso actual |
| 5 | 🟡 Medio | Infra BE | Rate limiting fijo (5/min login) impedía ejecutar la suite E2E completa (~15 logins por corrida) | `RATE_LIMIT_ENABLED` configurable vía env; **activo por defecto**, se desactiva solo para QA local (`docker-compose.yml`) |
| 6 | 🟡 Medio | Infra BE | Entrypoint rompía el contenedor por finales CRLF; migraciones fallaban contra BD creada con `create_all` | `.gitattributes` fuerza LF en `*.sh`; 3 migraciones idempotentes con guards `has_table()` |
| 7 | 🟢 Bajo | Tests BE | `test_not_triggered_for_servicio` fallaba: el mock no exponía `due_date` | Mock actualizado replicando el modelo real |

Todos los fixes están en commits atómicos con formato conventional commits
en la rama `feature/sprint7-edwin`.

---

## 4. Datos demo para la presentación (16.7)

Sembrados con `docker compose exec be python seed_roles.py` y
`python seed_test_data.py`:

| Dato | Valor |
|---|---|
| Usuario demo | `admin@bovitrack.com` / `Demo1234!` |
| Finca | Hacienda El Porvenir (FIN-DEMO-001) |
| Datos generados | 30 bovinos, pesos, producción lechera, eventos reproductivos, tratamientos, planes sanitarios, alimentación, inventario, movimientos y registros económicos de ~12 meses |
| Usuario desactivado (QA reactivación) | `exempleado@bovitrack.com` / `Demo1234!` |

Flujo completo verificado end-to-end: login → finca → módulos productivos →
dashboard económico con indicadores reales (HTTP 200) → reportes con descarga.

---

## 5. Documentación y Postman (16.8)

- `README.md`: módulos Alertas (HU014) y Auditoría (HU015) documentados;
  estructura de `qa_e2e/` y cómo ejecutar la suite.
- `docs/BoviTrack.postman_collection.json`:
  - **Auditoría (HU015):** listar logs filtrado, catálogo de acciones,
    export CSV, export Excel.
  - **Alertas y Notificaciones (HU014):** alertas activas, preferencias
    GET/PUT, historial (extrae `{{notificationId}}` automáticamente),
    marcar como leída.

---

## 6. Evidencias de cierre (16.9)

| Evidencia | Ubicación |
|---|---|
| Capturas E2E (30, todas OK) | `qa_e2e/screenshots/test_*_OK_*.png` |
| Este informe | `docs/SPRINTS/QA_CIERRE_SPRINT_08.md` |
| Estados del sprint actualizados | `docs/SPRINTS/SPRINT_08.md` (tareas 16.1–16.9 ✅) |
| Historial de commits QA | rama `feature/sprint7-edwin`, commits `922f56f..61c11ff` |

---

## 7. Pendientes FUERA del alcance de Edwin

Estos ítems quedan abiertos para sus respectivos dueños / el equipo:

- Self-QA funcional de HU014 → Tomás
- Self-QA funcional de HU015 → Camilo
- Demo final con el cliente (Luis Barbosa) — requiere HU014/HU015 integradas en main
- Tag de versión `v1.0.0` — al cierre conjunto del sprint

