"""
Módulo: modules/audit/exporters.py
¿Qué? Convierte registros de auditoría en un archivo CSV (con BOM, para que
      Excel en Windows muestre bien tildes y eñes) o en un Excel (.xlsx).
¿Impacto? Solo da formato: no consulta la BD ni decide qué registros salen.
"""

import csv
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app.modules.audit.schemas import AuditLogRecord

EXPORT_HEADERS = [
    "Fecha y hora",
    "Usuario",
    "Correo",
    "Accion",
    "Entidad",
    "ID entidad",
    "Finca",
    "Detalles",
]


def _record_to_row(record: AuditLogRecord) -> list[str]:
    """¿Qué? Convierte un registro de auditoría en una fila plana de texto.

    COMO: Administrador que abre el archivo descargado
    QUIERO: ver la fecha legible y el nombre del responsable, no identificadores
    PARA:   poder interpretar la evidencia sin consultar la base de datos.

    ¿Impacto? Los valores nulos se muestran como texto vacío o como
              "Usuario eliminado", nunca como "None".
    """
    return [
        record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        record.user_full_name or "Usuario eliminado",
        record.user_email or "",
        record.action,
        record.entity,
        record.entity_id or "",
        record.farm_name or "",
        record.details or "",
    ]


def export_to_csv(records: list[AuditLogRecord]) -> bytes:
    """¿Qué? Genera un archivo CSV con los registros recibidos.

    COMO: Administrador
    QUIERO: un archivo liviano que pueda abrir en cualquier herramienta
    PARA:   filtrar o cruzar los datos con otras fuentes rápidamente.

    ¿Impacto? Se codifica en UTF-8 con BOM (utf-8-sig) porque Excel en Windows
              muestra mal las tildes y las eñes si el archivo no lo lleva.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(EXPORT_HEADERS)
    for record in records:
        writer.writerow(_record_to_row(record))
    return buffer.getvalue().encode("utf-8-sig")


def export_to_excel(records: list[AuditLogRecord]) -> bytes:
    """¿Qué? Genera un archivo Excel (.xlsx) con los registros recibidos.

    COMO: Administrador que presenta la auditoría en una reunión
    QUIERO: un archivo con encabezados resaltados y columnas legibles
    PARA:   poder mostrarlo o imprimirlo sin tener que darle formato a mano.

    ¿Impacto? Usa la misma paleta institucional del módulo de reportes (HU013)
              para que los entregables del sistema se vean consistentes.
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Auditoria"

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="59930A", end_color="59930A", fill_type="solid")

    sheet.append(EXPORT_HEADERS)
    for cell in sheet[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for record in records:
        sheet.append(_record_to_row(record))

    # Anchos pensados para el contenido real de cada columna.
    for column, width in zip(
        ["A", "B", "C", "D", "E", "F", "G", "H"],
        [20, 28, 30, 22, 20, 38, 25, 60],
        strict=False,
    ):
        sheet.column_dimensions[column].width = width

    # Congelar la fila de encabezados para no perderla al desplazarse.
    sheet.freeze_panes = "A2"

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
