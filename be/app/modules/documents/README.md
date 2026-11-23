# Módulo `documents` — Gestión documental (HU012)

**Endpoints:** `/api/v1/farms/{farm_id}/documents`. Incluye subir (multipart), listar con búsqueda y paginación, descargar (`/{id}/download`) y eliminar.
**Tabla:** `document` (metadatos). **Archivos:** en `DOCUMENTS_STORAGE_DIR` (por defecto `storage/documents`).
**Permiso:** módulo `documentos` (propio; migración `r1s2t3u4v5w6`). **Rate limit:** 5/min para subir y eliminar, 20/min para listar y descargar.

| Archivo | Capa | Responsabilidad |
|---|---|---|
| `router.py` | HTTP | Lee el archivo por bloques (413 si supera 50 MB) y arma la descarga con `Content-Disposition` seguro. |
| `dependencies.py` | Composición | Elige el almacenamiento concreto (hoy disco local) y conecta ganado y auditoría. |
| `service.py` | Negocio | Subir, listar, descargar y eliminar. Coordina las validaciones, el almacenamiento y la BD. |
| `file_rules.py` | Reglas puras | Formato real por firma, Office sin macros, extensión coherente y nombre seguro. |
| `schemas.py` | Contrato | Enums de tipo y asociación, `DocumentResponse`, `DocumentListResponse` y el límite de 50 MB. |
| `storage.py` | Infraestructura | `LocalDocumentStorage`: guardar, leer y borrar bytes en disco. |
| `repository.py` | Datos | Metadatos activos de la finca, búsqueda y paginación. |
| `models.py` | Persistencia | Tabla ORM `Document`. |

## Conceptos de arquitectura

| Concepto | Respuesta para `documents` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | De guardar la evidencia documental de la finca (certificados, facturas, registros) asociada a la finca o a un bovino, y de entregarla de forma segura y trazable. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí, y está separada por razón de cambio: **qué archivo es aceptable** (`file_rules.py`), **dónde se guardan los bytes** (`storage.py`) y **qué metadatos se registran** (`repository.py`). Cada uno cambia por motivos distintos. Antes estaban mezclados en un solo archivo de 580 líneas y el router repetía validaciones. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Usa tres colaboradores inyectados: `DocumentStorage`, `BovineLookup` y `AuditRecorder`. Cambiar de disco local a la nube toca **una línea** de `dependencies.py`. |
| **Contrato** — ¿Qué garantiza? | **Entrada:** archivo de hasta 50 MB, con formato verificado por su contenido (nunca por la cabecera del cliente), coherente con el tipo elegido y con la extensión, y sin macros si es Office. **Errores:** archivo demasiado grande → `413`. Vacío, formato no permitido, tipo o extensión que no coincide, finca o bovino ajeno → `400` con mensaje en español. Documento inexistente, eliminado o de otra finca → `404 "Document not found"`. Archivo físico perdido → `404 "File not found"`. **Garantía:** si falla la BD después de guardar el archivo, el archivo se borra. Eliminar es lógico: el registro queda para la auditoría. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | El router solo llama a `upload_document(...)` y no sabe dónde terminan los bytes. El servicio solo conoce `save`, `read` y `delete`; no sabe si es un disco, S3 o una prueba en memoria. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia el disco salen bytes y una extensión, y vuelve un nombre interno generado por el servidor (`<uuid>_<timestamp>.<ext>`). El nombre del cliente nunca se usa como ruta. Hacia el cliente sale el nombre original saneado, solo en la cabecera de descarga. |

## Cambio de comportamiento intencional

- Si el disco falla al guardar o leer un archivo, la respuesta sigue siendo `500`, pero el mensaje ya no expone el error interno del sistema operativo. Antes decía `"Error saving file: <detalle del OS>"`.

## Bugs corregidos

- **Permiso propio `documentos`.** Antes los endpoints exigían el permiso de `bovinos`, y quien no tenía acceso a ganado no podía gestionar los documentos de la finca. La migración `r1s2t3u4v5w6` le da a cada rol los mismos permisos que tenía en `bovinos` (Administrador CRUD, Capataz CRU, Veterinario RU, Empleado R), así que nadie ganó ni perdió acceso. Desde ahora se ajustan por separado.
- **Eliminar ya no puede dejar documentos sin archivo.** El archivo físico se borra **después** del `commit`. Antes se borraba primero: si el commit fallaba, quedaba un documento activo cuya descarga respondía 404.

## Deuda conocida

- **Mensajes mezclados:** `"Document not found"` y `"File not found"` están en inglés y el resto en español.
