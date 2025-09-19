"""Controlador de reportes: JSON y PDF de rentabilidad."""

import io
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, jsonify, send_file, request
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)

from backend.db import DB

# Configuración para evitar problemas de backend gráfico
matplotlib.use("Agg")

# ===============================
# Blueprint
# ===============================
reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.route("/api/reportes/rentabilidad")
def rentabilidad_json():
    """
    Devuelve la rentabilidad mensual en formato JSON.

    Parámetros opcionales (query string):
        - inicio: fecha inicial en formato YYYY-MM-DD
        - fin: fecha final en formato YYYY-MM-DD
    """
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    consulta = """
        SELECT 
            TO_CHAR(DATE_TRUNC('month', v.fecha), 'YYYY-MM') AS mes,
            ROUND(SUM(dv.cantidad * dv.precio_unitario), 2) AS ingresos,
            ROUND(SUM(dc.cantidad * dc.precio_unitario), 2) AS costos,
            ROUND(SUM(dv.cantidad * dv.precio_unitario) 
                  - SUM(dc.cantidad * dc.precio_unitario), 2) AS utilidad,
            ROUND(
                ((SUM(dv.cantidad * dv.precio_unitario) 
                - SUM(dc.cantidad * dc.precio_unitario)) 
                / NULLIF(SUM(dv.cantidad * dv.precio_unitario),0)) * 100, 2
            ) AS margen_rentabilidad
        FROM ventas v
        JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        WHERE (%s IS NULL OR v.fecha >= %s)
          AND (%s IS NULL OR v.fecha <= %s)
        GROUP BY DATE_TRUNC('month', v.fecha)
        ORDER BY mes;
    """

    params = (inicio, inicio, fin, fin)
    data = DB.ejecutar_consulta(consulta, params, fetch_all=True)
    return jsonify(data)


@reportes_bp.route("/reportes/rentabilidad/pdf")
def rentabilidad_pdf():
    """
    Genera un PDF formal con gráfica, tabla y conclusión de rentabilidad.
    """

    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    consulta = """
        SELECT 
            TO_CHAR(DATE_TRUNC('month', v.fecha), 'YYYY-MM') AS mes,
            ROUND(SUM(dv.cantidad * dv.precio_unitario), 2) AS ingresos,
            ROUND(SUM(dc.cantidad * dc.precio_unitario), 2) AS costos,
            ROUND(SUM(dv.cantidad * dv.precio_unitario) 
                  - SUM(dc.cantidad * dc.precio_unitario), 2) AS utilidad
        FROM ventas v
        JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        WHERE (%s IS NULL OR v.fecha >= %s)
          AND (%s IS NULL OR v.fecha <= %s)
        GROUP BY DATE_TRUNC('month', v.fecha)
        ORDER BY mes;
    """

    params = (inicio, inicio, fin, fin)
    data = DB.ejecutar_consulta(consulta, params, fetch_all=True) or []

    if not inicio and data:
        inicio = data[0]["mes"] + "-01"
    if not fin and data:
        fin = data[-1]["mes"] + "-28"

    # --- Completar meses ---
    def generar_meses(inicio, fin):
        meses = []
        anio_i, mes_i = map(int, inicio.split("-")[:2])
        anio_f, mes_f = map(int, fin.split("-")[:2])

        fecha = datetime(anio_i, mes_i, 1)
        fecha_fin = datetime(anio_f, mes_f, 1)

        while fecha <= fecha_fin:
            meses.append(fecha.strftime("%Y-%m"))
            if fecha.month == 12:
                fecha = datetime(fecha.year + 1, 1, 1)
            else:
                fecha = datetime(fecha.year, fecha.month + 1, 1)
        return meses

    meses_completos = generar_meses(inicio, fin)
    data_dict = {row["mes"]: row for row in data}

    datos_finales = []
    for mes in meses_completos:
        if mes in data_dict:
            datos_finales.append({
                "mes": mes,
                "ingresos": float(data_dict[mes]["ingresos"]),
                "costos": float(data_dict[mes]["costos"]),
                "utilidad": float(data_dict[mes]["utilidad"]),
            })
        else:
            datos_finales.append({"mes": mes, "ingresos": 0.0, "costos": 0.0, "utilidad": 0.0})

    # --- Meses legibles ---
    meses_legibles = [
        datetime.strptime(row["mes"], "%Y-%m").strftime("%b %Y") for row in datos_finales
    ]

    ingresos = [row["ingresos"] for row in datos_finales]
    costos = [row["costos"] for row in datos_finales]
    utilidad = [row["utilidad"] for row in datos_finales]

    # --- Gráfica ---
    plt.figure(figsize=(8, 4))
    width = 0.25
    x = range(len(meses_legibles))

    plt.bar([i - width for i in x], ingresos, width=width, label="Ingresos", color="#2ecc71", alpha=0.8)
    plt.bar(x, costos, width=width, label="Costos", color="#e74c3c", alpha=0.8)
    plt.bar([i + width for i in x], utilidad, width=width, label="Utilidad", color="#3498db", alpha=0.8)

    plt.title("Rentabilidad Mensual", fontsize=14, fontweight="bold")
    plt.xlabel("Mes")
    plt.ylabel("Monto ($)")
    plt.xticks(x, meses_legibles, rotation=30)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png")
    plt.close()
    img_bytes.seek(0)

    # --- Conclusión ejecutiva ---
    utilidad_total = sum(utilidad) if utilidad else 0
    mes_max = meses_legibles[utilidad.index(max(utilidad))] if utilidad else "N/A"
    mes_min = meses_legibles[utilidad.index(min(utilidad))] if utilidad else "N/A"

    if utilidad_total > 0:
        conclusion = (
            f"La empresa es rentable con una utilidad acumulada de ${utilidad_total:.2f}. "
            f"El mejor mes fue {mes_max}, y el de menor rendimiento fue {mes_min}."
        )
    elif utilidad_total < 0:
        conclusion = (
            f"Se refleja una pérdida acumulada de ${abs(utilidad_total):.2f}. "
            f"El mes más desfavorable fue {mes_min}."
        )
    else:
        conclusion = "Los ingresos y costos se equilibraron, sin ganancias ni pérdidas."

    # --- Fecha y periodo ---
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M")
    periodo_text = f"Periodo: {meses_legibles[0]} a {meses_legibles[-1]}"

    # --- PDF ---
    pdf_bytes = io.BytesIO()
    doc = SimpleDocTemplate(pdf_bytes, pagesize=A4, title="Reporte de Rentabilidad")
    styles = getSampleStyleSheet()
    story = []

    # Encabezado bonito
    story.append(Paragraph("<b style='font-size:18pt'>Tienda Julio y Mary</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Reporte de Rentabilidad Mensual</b>", styles["Heading1"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(periodo_text, styles["Normal"]))
    story.append(Paragraph(f"Fecha de generación: {fecha_reporte}", styles["Normal"]))
    story.append(Spacer(1, 25))

    # Gráfica
    story.append(Paragraph("<b>📊 Gráfica de Rentabilidad</b>", styles["Heading2"]))
    story.append(Image(img_bytes, width=480, height=240))
    story.append(Spacer(1, 20))

    # Tabla con estilo
    story.append(Paragraph("<b>📑 Resultados Numéricos</b>", styles["Heading2"]))
    tabla_data = [["Mes", "Ingresos ($)", "Costos ($)", "Utilidad ($)"]]
    for mes, ing, cos, uti in zip(meses_legibles, ingresos, costos, utilidad):
        tabla_data.append([mes, f"{ing:.2f}", f"{cos:.2f}", f"{uti:.2f}"])

    tabla = Table(tabla_data, hAlign="CENTER", colWidths=[100, 100, 100, 100])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6fff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 20))

    # Conclusión destacada
    story.append(Paragraph("<b>📝 Conclusión Ejecutiva</b>", styles["Heading2"]))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<para backColor='#f8f9fa' spaceBefore=10 spaceAfter=10>{conclusion}</para>", styles["Normal"]))

    def add_footer(c, _doc):
        c.saveState()
        footer = f"Tienda Julio y Mary | Generado el {fecha_reporte}"
        c.setFont("Helvetica", 8)
        c.drawCentredString(A4[0] / 2.0, 15, footer)
        c.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    pdf_bytes.seek(0)

    nombre_pdf = f"rentabilidad_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"
    return send_file(pdf_bytes, as_attachment=True, download_name=nombre_pdf)

