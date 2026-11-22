# Módulo `audit` — Consulta de auditoría (HU015)

**Endpoints:**
- `GET /api/v1/admin/audit-logs`: listado filtrado y paginado.
- `GET /api/v1/admin/audit-logs/actions`: catálogo de acciones y entidades.
- `GET /api/v1/admin/audit-logs/export?export=csv|excel`: exportación.
- `GET /api/v1/farms/{farm_id}/audit-logs`: auditoría de una finca. Antes estaba escondida dentro de `routers/users.py`.

**Tablas propias:** ninguna. Es un **modelo de lectura** sobre `audit_log`, que vive en `app.core.audit_trail`, con cruces a `users`, `farm` y `user_farm`.
**Permisos:** la auditoría del sistema exige `usuarios:can_read` en al menos una finca. La de una finca exige `usuarios:can_read` en esa finca.

| Archivo | Responsabilidad |
|---|---|
| `router.py` | Dos `APIRouter` (sistema y por finca) unidos en `router`. |
| `dependencies.py` | Arma `AuditService` y el guard `require_audit_reader`. |
| `service.py` | Casos de uso: listar, catálogo, exportar y auditoría por finca. |
| `exporters.py` | CSV (con BOM) y Excel. Solo formato. |
| `repository.py` | Consultas de lectura y la traducción de filtros a SQL. |
| `schemas.py` | Filtros, registro, página, formato de exportación y `AuditLogResponse`. |

## Conceptos de arquitectura

| Concepto | Respuesta para `audit` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De **leer** la auditoría: quién modificó qué, cuándo y en qué finca, con filtros, paginación y exportación. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: consultar el rastro. **Escribirlo** no es de este módulo, sino de `app.core.audit_trail`: todos los módulos auditan, y si la escritura viviera aquí, todos dependerían de `audit`, y `audit` de ellos (un ciclo). Separar lectura y escritura por responsabilidad rompió ese ciclo. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | No importa código de identity ni de farms. Para mostrar nombres usa las tablas `users`, `farm` y `user_farm` desde `Base.metadata` (el esquema). Si cambian esas columnas, solo se revisa `repository.py`. |
| **Contrato** — ¿Qué garantiza? | Un usuario **solo ve la auditoría de sus fincas**. Pedir una finca ajena devuelve cero registros, nunca un error que revele que existe. Sin el permiso → `403 "No tienes permiso para consultar la auditoría del sistema"`. Exportar en JSON → `400`. Se exportan como máximo 10 000 registros. La auditoría por finca muestra los últimos 500 cambios de datos, sin eventos de sesión. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | El router pide `list_audit_logs`, `export` o `farm_logs`. No sabe que hay cruces SQL ni cómo se arma un `.xlsx`. El repositorio tampoco conoce los schemas: declara los filtros que necesita con un `Protocol` (`AuditFilterValues`). |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Salen schemas de solo lectura o bytes de un archivo. No entra ningún modelo ORM de otros módulos. |
