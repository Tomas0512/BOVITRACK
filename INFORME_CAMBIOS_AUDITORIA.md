# Revisión de auditoría y cambios aplicados — BoviTrack

**Fecha:** 13 de noviembre de 2026  
**Documento revisado:** `🔒 AUDITORÍA DE SEGURIDAD Y ARQUITECTURA BOVITRACK.docx`

## Evaluación del documento

La auditoría sirve como lista de temas a verificar, pero algunas afirmaciones no coinciden con el código y otras son recomendaciones futuras, no vulnerabilidades demostradas:

| Hallazgo del documento | Evaluación en el código |
|---|---|
| Inyección SQL crítica al elegir vistas de reportes | **La explotación descrita no estaba disponible por HTTP:** el nombre de vista se elegía con constantes internas, no con un parámetro del usuario. Aun así, limitar expresamente las vistas permitidas es una defensa adicional adecuada y ya quedó aplicado. |
| Documentos sin validación | **Parcialmente cierto:** ya existían un límite de 50 MB y una lista de MIME permitidos, pero el MIME se confiaba al cliente y el archivo se leía completo antes de limitarlo. Se corrigieron esos puntos y se endureció el manejo del nombre y la descarga. |
| Validación débil en todos los schemas | **Generalización excesiva:** ya había validaciones en los schemas de fincas, usuarios y pesajes. Se añadieron límites de tamaño y rango a campos de bovinos y pesajes que carecían de ellos; queda como trabajo futuro revisar los demás schemas uno por uno. |
| Secretos de ejemplo expuestos | **Parcialmente cierto:** los archivos `.env` locales están ignorados por Git; la plantilla raíz ya usaba marcadores, pero la plantilla `be/.env.example` incluía una clave débil. Ambas plantillas ahora dejan la clave vacía y explican cómo generar una propia. El backend exige al menos 32 caracteres. |
| Falta de `iat` en JWT como riesgo de renovación anormalmente rápida | **Mejora útil, impacto descrito incorrectamente:** la ausencia de `iat` no permitía por sí sola renovar tokens más rápido. Se añadió la marca temporal de emisión a access y refresh tokens como metadato estándar. |
| CSRF necesario para formularios | **No lo recomiendo para el flujo actual:** los JWT se envían en la cabecera `Authorization`, que el navegador no adjunta automáticamente como sí puede hacer con cookies. La protección propuesta no corresponde a la arquitectura actual. |
| TLS, HSTS, Redis, colas y tracing | Son recomendaciones para una preparación de producción y operación a mayor escala. TLS/HSTS dependen del despliegue; Redis, colas y tracing deberían priorizarse con métricas o requisitos concretos. |
| Transacciones de auditoría | **Confirmado en bovinos:** crear y actualizar confirmaban el cambio antes de escribir el log, permitiendo que fallara la auditoría después del cambio. Se hicieron atómicas las operaciones de crear, actualizar y retirar bovinos. Otros servicios también requieren una revisión transaccional independiente. |

## Cambios implementados

- **Carga de documentos:** lectura limitada por bloques al máximo de 50 MiB; detección de PDF, imágenes, texto y paquetes Office a partir del contenido; rechazo de extensiones o categorías incompatibles y de macros en paquetes Office; sanitización del nombre original; descarga como adjunto con `nosniff` y nombre codificado de forma segura.
- **Compatibilidad de Office:** ampliación de `document.mime_type` a 100 caracteres en el modelo y mediante la migración `q1r2s3t4u5v6`, necesaria porque los MIME oficiales de DOCX/XLSX superan los 50 caracteres anteriores.
- **Límite en nginx:** `client_max_body_size` de 51 MiB para permitir el límite del archivo más el overhead de `multipart` cuando el tráfico pasa por el proxy.
- **Consistencia de documentos:** si falla la escritura de metadata o auditoría, se revierte la transacción y se elimina el archivo que se alcanzó a guardar.
- **Reportes:** allowlist explícita de vistas disponibles y binding expansible de los IDs de finca. No se construyen los parámetros de IDs a mano.
- **JWT y secretos:** clave de firma con longitud mínima de 32 caracteres; `iat` incluido en access y refresh tokens; plantillas de entorno sin una clave débil de ejemplo.
- **Validación de entradas:** límites de longitud para campos de bovinos, pesos máximos de 2.500 kg para bovinos/pesajes y límite de observaciones.
- **Auditoría de bovinos:** create, update y delete/soft-delete escriben el registro de auditoría en la misma transacción que el cambio, con rollback si ocurre un error.
- **Regresión:** se agregó `be/tests/test_security_hardening.py` con pruebas de clave, JWT, allowlist SQL, firmas de archivos, extensión, nombre de archivo y atomicidad de auditoría.

## Verificación ejecutada

- `pytest`: **10 pruebas aprobadas** (`be/tests/test_security_hardening.py`).
- `ruff check`: aprobado en los archivos modificados de Python.
- `python -m compileall -q app tests`: aprobado.
- `git diff --check`: aprobado.

Las pruebas muestran advertencias deprecadas originadas por dependencias existentes (`reportlab` y `python-jose`); no son fallos de las pruebas.

## Recomendaciones pendientes

1. En despliegue real, terminar TLS antes de habilitar HSTS y gestionar/rotar secretos fuera de archivos del repositorio. Generar `SECRET_KEY` distinta para cada entorno con el comando indicado en los `.env.example`.
2. Añadir escaneo antimalware al flujo de documentos antes de producción. La validación de firmas reduce archivos disfrazados, pero no certifica que un documento sea inocuo.
3. Revisar y hacer atómicas las operaciones de los demás servicios que aún confirmen el registro principal antes de escribir su auditoría.
4. Completar límites de entrada y paginación donde falten, y evaluar rate limiting/índices/caché con métricas de uso.
5. Definir backups con pruebas de restauración, monitoreo y un procedimiento de respuesta a incidentes para el entorno productivo.
