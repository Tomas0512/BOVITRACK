"""
Capa core: infraestructura transversal de BoviTrack (configuración, base de datos,
seguridad, correo, rate limiting y traducción de errores). Ver README.md.

No se re-exporta nada aquí a propósito: importar app.core.config dispara la
validación de variables de entorno, y eso debe pasar solo cuando se necesita.
"""
