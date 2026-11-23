"""
Módulo: modules/reports/exporters.py
¿Qué? Convierte un ReportResponse en un archivo Excel (.xlsx) o PDF.
¿Para qué? Que el ganadero descargue o imprima el reporte.
¿Impacto? Solo da formato: no consulta la BD ni calcula nada. Si mañana se
          agrega CSV, se escribe aquí una función más sin tocar el servicio.
"""

import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)

from app.modules.reports.schemas import ReportResponse


def export_to_excel(report: ReportResponse) -> bytes:
    wb = Workbook()
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="59930A", end_color="59930A", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    def write_section(ws, title: str, headers: list[str], rows: list[list]):
        ws.append([title])
        ws[f"A{ws.max_row}"].font = Font(bold=True, size=13, color="1B4332")
        ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=len(headers))
        ws.append(headers)
        for cell in ws[ws.max_row]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border
        for row_data in rows:
            ws.append(row_data)
            for cell in ws[ws.max_row]:
                cell.border = thin_border
        ws.append([])

    # Productive sheet
    if report.productive:
        ws = wb.active
        ws.title = "Productivo"
        p = report.productive
        write_section(ws, "Resumen Productivo", ["Indicador", "Valor"], [
            ["Total Bovinos", p.total_bovines],
            ["Machos", p.males],
            ["Hembras", p.females],
            ["Peso Promedio", p.avg_weight or 0],
            ["Total Leche (L)", p.total_milk_liters],
            ["Total Terneros", p.total_calves],
        ])
        if p.calves_by_age_group:
            age_rows = [[g, str(c)] for g, c in p.calves_by_age_group.items()]
            write_section(ws, "Terneros por Edad", ["Grupo", "Cantidad"], age_rows)
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 20

    # Sanitary sheet
    if report.sanitary:
        ws = wb.create_sheet("Sanitario")
        s = report.sanitary
        write_section(ws, "Resumen Sanitario", ["Indicador", "Valor"], [
            ["Total Tratamientos", s.total_treatments],
            ["Planes Activos", s.active_sanitary_plans],
            ["Pendientes", s.pending_treatments],
        ])
        if s.treatments_by_type:
            type_rows = [[t, str(c)] for t, c in s.treatments_by_type.items()]
            write_section(ws, "Tratamientos por Tipo", ["Tipo", "Cantidad"], type_rows)
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 20

    # Economic sheet
    if report.economic:
        ws = wb.create_sheet("Economico")
        e = report.economic
        write_section(ws, "Resumen Economico", ["Indicador", "Valor"], [
            ["Total Ingresos", f"${e.total_income:,.2f}"],
            ["Total Egresos", f"${e.total_expense:,.2f}"],
            ["Balance", f"${e.balance:,.2f}"],
        ])
        if e.income_by_activity:
            inc_rows = [[a, f"${v:,.2f}"] for a, v in e.income_by_activity.items()]
            write_section(ws, "Ingresos por Actividad", ["Actividad", "Monto"], inc_rows)
        if e.expense_by_activity:
            exp_rows = [[a, f"${v:,.2f}"] for a, v in e.expense_by_activity.items()]
            write_section(ws, "Egresos por Actividad", ["Actividad", "Monto"], exp_rows)
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 20

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_to_pdf(report: ReportResponse) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=16, textColor=colors.HexColor("#1B4332"))
    section_style = ParagraphStyle("Section2", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#59930A"))
    normal = styles["Normal"]

    elements = [Paragraph(f"Reporte - {report.farm_name}", title_style)]
    elements.append(Spacer(1, 12))
    if report.category:
        elements.append(Paragraph(f"Categoria: {report.category.value}", normal))
    if report.start_date:
        elements.append(Paragraph(f"Desde: {report.start_date}", normal))
    if report.end_date:
        elements.append(Paragraph(f"Hasta: {report.end_date}", normal))
    elements.append(Spacer(1, 12))

    GREEN = colors.HexColor("#59930A")
    WHITE = colors.white
    LIGHT_GREEN = colors.HexColor("#E8F5E9")

    def add_table(title: str, headers: list[str], data_rows: list[list]):
        elements.append(Paragraph(title, section_style))
        elements.append(Spacer(1, 6))
        table_data = [headers] + data_rows
        t = Table(table_data, colWidths=[120 * mm, 80 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GREEN),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    if report.productive:
        p = report.productive
        add_table("Resumen Productivo", ["Indicador", "Valor"], [
            ["Total Bovinos", str(p.total_bovines)],
            ["Machos", str(p.males)],
            ["Hembras", str(p.females)],
            ["Peso Promedio", str(p.avg_weight or 0)],
            ["Total Leche (L)", f"{p.total_milk_liters:.1f}"],
            ["Total Terneros", str(p.total_calves)],
        ])

    if report.sanitary:
        s = report.sanitary
        add_table("Resumen Sanitario", ["Indicador", "Valor"], [
            ["Total Tratamientos", str(s.total_treatments)],
            ["Planes Activos", str(s.active_sanitary_plans)],
            ["Pendientes", str(s.pending_treatments)],
        ])

    if report.economic:
        e = report.economic
        add_table("Resumen Economico", ["Indicador", "Valor"], [
            ["Total Ingresos", f"${e.total_income:,.2f}"],
            ["Total Egresos", f"${e.total_expense:,.2f}"],
            ["Balance", f"${e.balance:,.2f}"],
        ])

    doc.build(elements)
    buf.seek(0)
    return buf.getvalue()
