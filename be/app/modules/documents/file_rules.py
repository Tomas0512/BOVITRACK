"""
Módulo: modules/documents/file_rules.py
¿Qué? Reglas sobre el CONTENIDO de un archivo: qué formato es de verdad (por su
      firma, no por lo que dice el cliente), si un Office trae macros, si la
      extensión coincide con el contenido y cómo limpiar el nombre original.
¿Para qué? Que no se puedan subir ejecutables disfrazados, documentos con macros
           ni nombres que escapen del directorio o inyecten cabeceras HTTP.
¿Impacto? Son funciones puras (sin BD, sin disco, sin HTTP): se prueban con bytes
          en memoria. Si una regla falla lanzan BusinessRuleError (400).
"""

import io
import zipfile
from pathlib import Path

from app.modules.documents.schemas import MAX_DOCUMENT_SIZE
from app.shared.exceptions import BusinessRuleError


def sanitize_original_filename(filename: str | None) -> str:
    """Strip path components and control characters from client-provided names."""
    candidate = (filename or "document").replace("\\", "/").split("/")[-1]
    candidate = "".join(char for char in candidate if char.isprintable()).strip(" .")
    return (candidate or "document")[:255]


def detect_mime_type(file_content: bytes, declared_mime: str = "") -> str:
    """Identify supported formats from their content, not from the HTTP header."""
    if len(file_content) > MAX_DOCUMENT_SIZE or not file_content:
        raise BusinessRuleError("Tamaño de archivo no permitido")

    if file_content.startswith(b"%PDF-"):
        return "application/pdf"
    if file_content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"

    if file_content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        legacy_mime = declared_mime.split(";", 1)[0].strip().lower()
        if legacy_mime in {"application/msword", "application/vnd.ms-excel"}:
            return legacy_mime
        raise BusinessRuleError("No se pudo determinar si el archivo Office es Word o Excel")

    if zipfile.is_zipfile(io.BytesIO(file_content)):
        try:
            with zipfile.ZipFile(io.BytesIO(file_content)) as archive:
                entries = archive.infolist()
                names = {entry.filename for entry in entries}
                uncompressed_size = sum(entry.file_size for entry in entries)
                if len(entries) > 1000 or uncompressed_size > 100 * 1024 * 1024:
                    raise BusinessRuleError("El paquete Office tiene una estructura no permitida")
                if "word/document.xml" in names and "[Content_Types].xml" in names:
                    if any(name.endswith("vbaProject.bin") for name in names):
                        raise BusinessRuleError("No se permiten documentos Office con macros")
                    return (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )
                if "xl/workbook.xml" in names and "[Content_Types].xml" in names:
                    if any(name.endswith("vbaProject.bin") for name in names):
                        raise BusinessRuleError("No se permiten documentos Office con macros")
                    return (
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
        except zipfile.BadZipFile:
            pass

    try:
        decoded = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = ""
    if decoded and all(
        character.isprintable() or character in "\t\n\r\f" for character in decoded
    ):
        if declared_mime.split(";", 1)[0].strip().lower() == "text/csv":
            return "text/csv"
        return "text/plain"

    raise BusinessRuleError("Formato de archivo no permitido o contenido no reconocido")


def validate_file_extension(filename: str, mime_type: str) -> None:
    """Reject misleading names whose suffix contradicts the detected content."""
    allowed_extensions = {
        "application/pdf": {".pdf"},
        "image/jpeg": {".jpg", ".jpeg"},
        "image/png": {".png"},
        "image/gif": {".gif"},
        "application/msword": {".doc"},
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
            ".docx"
        },
        "application/vnd.ms-excel": {".xls"},
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
            ".xlsx"
        },
        "text/plain": {".txt"},
        "text/csv": {".csv"},
    }
    if Path(filename).suffix.lower() not in allowed_extensions.get(mime_type, set()):
        raise BusinessRuleError("La extensión del archivo no coincide con su contenido")


def get_file_extension(mime_type: str) -> str:
    """
    What? Gets file extension from MIME type.
    Why? Save files with correct extension.
    """
    mime_to_ext = {
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/csv": "csv",
    }
    return mime_to_ext.get(mime_type, "bin")


# Qué contenidos (MIME detectado) acepta cada tipo de documento elegido por el usuario.
# Antes vivía en el router; es una regla de negocio, por eso está aquí.
EXPECTED_MIME_BY_DOCUMENT_TYPE: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "image": {"image/jpeg", "image/png", "image/gif"},
    "word": {
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    "excel": {
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
    "text": {"text/plain", "text/csv"},
}


def ensure_mime_matches_document_type(detected_mime: str, document_type: str) -> None:
    """El contenido real debe corresponder al tipo de documento declarado."""
    if detected_mime not in EXPECTED_MIME_BY_DOCUMENT_TYPE[document_type]:
        raise BusinessRuleError("El contenido del archivo no coincide con el tipo permitido")
