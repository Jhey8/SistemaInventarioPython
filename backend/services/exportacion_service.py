import io

import pandas as pd
from fpdf import FPDF

def _latin1(texto):
    return str(texto).encode("latin-1", "replace").decode("latin-1")

def _formato_celda(valor):
    if isinstance(valor, float):
        return f"{valor:,.2f}"
    return "" if valor is None else str(valor)

def generar_excel(tablas):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for nombre, df in tablas:
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
            _ajustar_anchos(writer.sheets[nombre[:31]], df)
    buffer.seek(0)
    return buffer

def _ajustar_anchos(hoja, df):
    for i, columna in enumerate(df.columns, start=1):
        largo = max([len(str(columna))] + [len(str(v)) for v in df[columna]] + [8])
        hoja.column_dimensions[chr(64 + i) if i <= 26 else "AA"].width = min(largo + 3, 40)

def generar_pdf(titulo, tablas):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, _latin1(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, _latin1("Sistema de Inventario · reporte generado automáticamente"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(20, 20, 20)
    pdf.ln(3)

    for subtitulo, df in tablas:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, _latin1(subtitulo), new_x="LMARGIN", new_y="NEXT")
        _tabla_pdf(pdf, df)
        pdf.ln(5)

    return io.BytesIO(bytes(pdf.output()))

def _tabla_pdf(pdf, df):
    columnas = list(df.columns)
    if not columnas:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 7, _latin1("Sin datos."), new_x="LMARGIN", new_y="NEXT")
        return

    ancho_util = pdf.w - 2 * pdf.l_margin
    ancho = ancho_util / len(columnas)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(235, 237, 240)
    for col in columnas:
        pdf.cell(ancho, 7, _latin1(col)[:22], border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for _, fila in df.iterrows():
        for col in columnas:
            pdf.cell(ancho, 6, _latin1(_formato_celda(fila[col]))[:22], border=1)
        pdf.ln()
