# Evidencias · Fase 1 — BoviTrack

**Fecha:** 13 de noviembre de 2026  
**Ambiente:** API local `http://localhost:8000`; backend y PostgreSQL Docker healthy.  
**Versión:** commit base `e097f28`, rama `ultimos-cambios`, árbol de trabajo modificado localmente.  
**Mecanismo:** llamadas HTTP locales con Python `urllib`; no se incluyeron credenciales ni tokens.

## Preparación de acceso

1. Se autenticó la cuenta QA definida en `qa_e2e/config.py` mediante `POST /api/v1/auth/login`; respuesta `200` (token omitido).
2. El UUID de finca que estaba configurado inicialmente en QA respondió `403: No tienes acceso a esta finca` al consultar bovinos.
3. Se consultó `GET /api/v1/farms` con la misma cuenta y se seleccionó una finca accesible: `82a7b0cd-7a24-4a30-bc45-d7fb68e07a86`.

## Evidencia A · Consulta

**Solicitud ejecutada**

```http
GET /api/v1/farms/82a7b0cd-7a24-4a30-bc45-d7fb68e07a86/bovines
Authorization: Bearer [omitido]
```

**Respuesta observada:** `HTTP 200`, cuerpo JSON de tipo arreglo con **30 bovinos** antes de registrar la prueba. Se capturaron los nombres de campos del `BovineResponse` (26 campos); por privacidad, no se copian datos de animales existentes.

## Evidencia B · Escritura

**Solicitud ejecutada**

```http
POST /api/v1/farms/82a7b0cd-7a24-4a30-bc45-d7fb68e07a86/bovines
Authorization: Bearer [omitido]
Content-Type: application/json
```

```json
{
  "identification_number": "ARQ-F1-20261113-01",
  "name": "Bovino temporal actividad arquitectura",
  "sex": "hembra",
  "breed": "Criollo",
  "birth_date": "2024-11-13",
  "birth_weight": 32.5,
  "current_weight": 280.0,
  "purpose": "carne",
  "entry_type": "compra",
  "entry_date": "2025-11-13",
  "observations": "Registro temporal de verificación Fase 1"
}
```

**Respuesta observada:** `HTTP 201 Created`. Fragmento de la respuesta real (se omite `registered_by`):

```json
{
  "id": "89750938-1bd1-4b30-bf94-23a0ad24bcc3",
  "farm_id": "82a7b0cd-7a24-4a30-bc45-d7fb68e07a86",
  "identification_number": "ARQ-F1-20261113-01",
  "sex": "hembra",
  "breed": "Criollo",
  "birth_date": "2024-11-13",
  "birth_weight": "32.50",
  "current_weight": "280.00",
  "purpose": "carne",
  "status": "activo",
  "entry_type": "compra",
  "entry_date": "2025-11-13",
  "is_active": true
}
```

**Verificación posterior:** otra consulta `GET` respondió `200`, con 31 elementos y el bovino creado presente.

## Limpieza del registro de prueba

Se llamó `DELETE /api/v1/farms/82a7b0cd-7a24-4a30-bc45-d7fb68e07a86/bovines/89750938-1bd1-4b30-bf94-23a0ad24bcc3`; respuesta `204 No Content`. Es un soft delete: no elimina físicamente la fila ni su auditoría. La consulta posterior respondió `200` y el bovino ya no figuraba en la lista activa.

## Trazabilidad de llamadas

| Operación / paso | Archivo y función | Responsabilidad | Evidencia (líneas) |
|---|---|---|---|
| GET 1 | `FarmDetailPage.renderTab()` | Presenta la pestaña de bovinos | `fe/src/pages/FarmDetailPage.tsx:68–71` |
| GET 2 | `BovineList.fetchData()` | Inicia carga y controla estado/error | `fe/src/components/bovines/BovineList.tsx:324–354` |
| GET 3 | `listBovines()` | Ejecuta petición Axios | `fe/src/api/bovines.ts:53–60` |
| GET 4 | `routers.bovines.list_all()` | Endpoint, permiso y serialización | `be/app/routers/bovines.py:123–138` |
| GET 5 | `bovine_service.list_bovines()` | Query por finca, activo, filtros y orden | `be/app/services/bovine_service.py:127–147` |
| POST 1 | `BovineFormModal.handleSubmit()` / `createBovine()` | Construye body y envía POST | `BovineFormModal.tsx:163–188`; `api/bovines.ts:73–76` |
| POST 2 | `routers.bovines.create()` | Dependencias de seguridad, llama servicio y devuelve schema | `be/app/routers/bovines.py:33–45` |
| POST 3 | `BovineCreate` | Valida contrato y reglas implementadas en schema | `be/app/schemas/bovine.py:17–91` |
| POST 4 | `bovine_service.create_bovine()` | Unicidad, referencias, persistencia y transacción | `be/app/services/bovine_service.py:45–124` |
| POST 5 | `add_audit_log()` | Añade el evento de auditoría | `be/app/services/audit_service.py:20–40` |

## Referencia de versión y limitaciones de evidencia

La última revisión Git mostró `e097f28` como commit base y modificaciones locales sin commit, incluidas modificaciones en archivos de bovinos. Por ello, la versión probada se identifica como **commit base + árbol de trabajo local**, no solo como el commit publicado. La evidencia es el registro de solicitudes/respuestas HTTP; no se adjuntan capturas de navegador porque la comprobación se ejecutó directamente contra la API.
