"""
Módulo: modules/documents/storage.py (adaptador de infraestructura)
¿Qué? Guarda, lee y borra los bytes de los documentos en el disco local.
¿Para qué? Separar *dónde* viven los archivos de *qué* se hace con ellos. El
           servicio solo conoce la interfaz DocumentStorage (save, read, delete).
¿Impacto? Para desplegar con otro almacenamiento (S3, Azure Blob, un volumen
          compartido...) basta con escribir otra clase con estos tres métodos
          y conectarla en dependencies.py. El servicio y sus pruebas no cambian.
          El directorio se configura con DOCUMENTS_STORAGE_DIR (core/config.py).
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.shared.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class LocalDocumentStorage:
    """Implementación de DocumentStorage sobre un directorio del servidor."""

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, extension: str) -> str:
        """Guarda el archivo y devuelve el nombre interno: <uuid>_<timestamp>.<ext>.

        El nombre lo genera el servidor (nunca el cliente), así no hay colisiones
        ni rutas maliciosas. Un error de disco se propaga como error 500.
        """
        stored_filename = f"{uuid.uuid4()}_{int(datetime.now(timezone.utc).timestamp())}.{extension}"
        (self._base_dir / stored_filename).write_bytes(content)
        return stored_filename

    def read(self, stored_filename: str) -> bytes:
        """Devuelve los bytes del archivo. NotFoundError si ya no está en disco."""
        file_path = self._base_dir / stored_filename
        if not file_path.exists():
            raise NotFoundError("File not found")
        return file_path.read_bytes()

    def delete(self, stored_filename: str) -> None:
        """Borra el archivo si existe. Un fallo se registra pero no interrumpe:
        el documento ya quedó marcado como eliminado en la base de datos."""
        file_path = self._base_dir / stored_filename
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as exc:
                logger.warning("No se pudo borrar el archivo físico %s: %s", stored_filename, exc)
