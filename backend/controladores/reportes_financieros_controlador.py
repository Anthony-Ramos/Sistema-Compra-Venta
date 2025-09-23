"""Controlador de reportes financieros detallados con rango de fechas.
Incluye endpoints JSON para gráficas interactivas y endpoints PDF con reportes formales.
"""

from datetime import datetime, timedelta
import io
import locale

import matplotlib.pyplot as plt
from flask import Blueprint, jsonify, request, send_file
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from backend.db import DB

financieros_bp = Blueprint("financieros", __name__)

# Aseguramos que los meses se muestren en español abreviado
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    # fallback en caso de que no esté disponible en Windows
    locale.setlocale(locale.LC_TIME, "Spanish_Spain")

# ===============================
# Auxiliares
# ===============================
def parse_mes(valor, inicio=True):
    """Convierte un valor tipo 'YYYY-MM' en fecha inicio o fin de mes."""
    if not valor:
        return None
    try:
        fecha = datetime.strptime(valor, "%Y-%m")
        if inicio:
            return fecha.date().replace(day=1)  # Primer día del mes
        year, month = fecha.year, fecha.month
        if month == 12:
            return datetime(year, 12, 31).date()
        next_month = datetime(year, month + 1, 1).date()
        return next_month - timedelta(days=1)
    except ValueError as err:
        print("Error al parsear mes:", err)
        return None


def generar_meses(inicio, fin):
    """Genera un rango de meses entre inicio y fin (YYYY-MM)."""
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

def formatear_meses(datos):
    """Convierte 'YYYY-MM' a 'Mes abreviado Año' en español (ej: sep. 2025)."""
    meses_es = {
        1: "ene.", 2: "feb.", 3: "mar.", 4: "abr.", 5: "may.",
        6: "jun.", 7: "jul.", 8: "ago.", 9: "sep.", 10: "oct.",
        11: "nov.", 12: "dic."
    }
    for row in datos:
        if "mes" in row and row["mes"]:
            try:
                fecha = datetime.strptime(row["mes"], "%Y-%m")
                row["mes"] = f"{meses_es[fecha.month]} {fecha.year}"
            except Exception:
                pass
    return datos

# ===============================
# Endpoints JSON
# ===============================

@financieros_bp.route("/api/finanzas/estado_resultados")
def estado_resultados():
    """
    Devuelve el estado de resultados mensual (Ingresos, Costos y Utilidad).

    Parámetros (query string):
        - inicio (str, formato YYYY-MM): mes de inicio del rango.
        - fin (str, formato YYYY-MM): mes de fin del rango.

    Respuesta JSON:
        [
            {
                "mes": "Ago 2025",
                "ingresos": 120.50,
                "costos": 40.00,
                "utilidad": 80.50
            },
            ...
        ]
    """
    inicio = parse_mes(request.args.get("inicio"), True)
    fin = parse_mes(request.args.get("fin"), False)
    consulta = """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS costos,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario) - 
                     SUM(dc.cantidad * dc.precio_unitario), 0) AS utilidad
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
    """
    try:
        datos = DB.ejecutar_consulta(consulta, (inicio, fin), fetch_all=True)
        return jsonify(formatear_meses(datos))
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@financieros_bp.route("/api/finanzas/margen")
def margen_rentabilidad():
    """
    Devuelve el margen de rentabilidad mensual (%).

    Parámetros (query string):
        - inicio (str, formato YYYY-MM): mes de inicio del rango.
        - fin (str, formato YYYY-MM): mes de fin del rango.

    Respuesta JSON:
        [
            {
                "mes": "Ago 2025",
                "margen": 65.33
            },
            ...
        ]
    """
    inicio = parse_mes(request.args.get("inicio"), True)
    fin = parse_mes(request.args.get("fin"), False)
    consulta = """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            ROUND((
                COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) - 
                COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
            ) / NULLIF(COALESCE(SUM(dv.cantidad * dv.precio_unitario),0),0) * 100, 2) AS margen
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
    """
    try:
        datos = DB.ejecutar_consulta(consulta, (inicio, fin), fetch_all=True)
        return jsonify(formatear_meses(datos))
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@financieros_bp.route("/api/finanzas/flujo")
def flujo_caja():
    """
    Devuelve el flujo de caja mensual (Ingresos, Egresos y Flujo Neto).

    Parámetros (query string):
        - inicio (str, formato YYYY-MM): mes de inicio del rango.
        - fin (str, formato YYYY-MM): mes de fin del rango.

    Respuesta JSON:
        [
            {
                "mes": "Ago 2025",
                "ingresos": 150.00,
                "egresos": 50.00,
                "flujo_neto": 100.00
            },
            ...
        ]
    """
    inicio = parse_mes(request.args.get("inicio"), True)
    fin = parse_mes(request.args.get("fin"), False)
    consulta = """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS egresos,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) - 
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS flujo_neto
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
    """
    try:
        datos = DB.ejecutar_consulta(consulta, (inicio, fin), fetch_all=True)
        return jsonify(formatear_meses(datos))
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@financieros_bp.route("/api/finanzas/equilibrio")
def punto_equilibrio():
    """
    Devuelve el estado de equilibrio mensual (Ingresos, Costos y Estado).

    Parámetros (query string):
        - inicio (str, formato YYYY-MM): mes de inicio del rango.
        - fin (str, formato YYYY-MM): mes de fin del rango.

    Respuesta JSON:
        [
            {
                "mes": "Ago 2025",
                "ingresos": 120.00,
                "costos": 90.00,
                "estado": "Utilidad"   # Puede ser "Utilidad", "Pérdida" o "Equilibrio"
            },
            ...
        ]
    """
    inicio = parse_mes(request.args.get("inicio"), True)
    fin = parse_mes(request.args.get("fin"), False)
    consulta = """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS costos,
            CASE 
                WHEN COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) > 
                     COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
                    THEN 'Utilidad'
                WHEN COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) < 
                     COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
                    THEN 'Pérdida'
                ELSE 'Equilibrio'
            END AS estado
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
    """
    try:
        datos = DB.ejecutar_consulta(consulta, (inicio, fin), fetch_all=True)
        return jsonify(formatear_meses(datos))
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@financieros_bp.route("/api/finanzas/crecimiento")
def crecimiento():
    """
    Devuelve el crecimiento porcentual de las ventas mensuales.

    Parámetros (query string):
        - inicio (str, formato YYYY-MM): mes de inicio del rango.
        - fin (str, formato YYYY-MM): mes de fin del rango.

    Respuesta JSON:
        [
            {
                "mes": "Ago 2025",
                "ingresos": 130.00,
                "crecimiento": 15.38   # Porcentaje comparado al mes anterior
            },
            ...
        ]
    """
    inicio = parse_mes(request.args.get("inicio"), True)
    fin = parse_mes(request.args.get("fin"), False)
    consulta = """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        ), ingresos AS (
            SELECT 
                DATE_TRUNC('month', v.fecha)::date AS mes,
                SUM(dv.cantidad * dv.precio_unitario) AS ingresos
            FROM ventas v
            JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
            WHERE v.fecha BETWEEN %s AND %s
            GROUP BY DATE_TRUNC('month', v.fecha)
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(i.ingresos, 0) AS ingresos,
            ROUND(
                (
                    (COALESCE(i.ingresos,0) - 
                     LAG(COALESCE(i.ingresos,0)) OVER (ORDER BY m.mes)) 
                    / NULLIF(
                        LAG(COALESCE(i.ingresos,0)) OVER (ORDER BY m.mes),0
                    )
                ) * 100, 2
            ) AS crecimiento
        FROM meses m
        LEFT JOIN ingresos i ON m.mes = i.mes
        ORDER BY m.mes;
    """
    try:
        datos = DB.ejecutar_consulta(consulta, (inicio, fin, inicio, fin), fetch_all=True)
        return jsonify(formatear_meses(datos))
    except Exception as err:
        return jsonify({"error": str(err)}), 500



# ===============================
# Endpoints PDF
# ===============================
@financieros_bp.route("/reportes/general/pdf")
def reporte_general_pdf():
    """Genera un PDF único con todos los reportes financieros (incluye meses sin registros)."""
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    inicio_date = parse_mes(inicio, True)
    fin_date = parse_mes(fin, False)

    pdf_bytes = io.BytesIO()
    doc = SimpleDocTemplate(pdf_bytes, pagesize=A4, title="Reporte General")
    styles = getSampleStyleSheet()
    story = []

    # ====== Encabezado ======
    story.append(Paragraph("<b>Tienda Julio y Mary</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("📑 Reporte General Financiero", styles["Heading1"]))
    story.append(Paragraph(f"Periodo: {inicio_date} a {fin_date}", styles["Normal"]))
    story.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 30))

    # ✅ Función para dar formato de dos decimales
    def format_decimal(valor):
        try:
            val = float(valor)
            # return "N/A" if val == 0 else f"{val:.2f}"  # Descomenta si querés que 0 sea N/A
            return f"{val:.2f}"
        except:
            return str(valor)

    # 🔹 Helper: Agregar secciones con tabla + gráfica + conclusión
    def agregar_reporte(
        titulo, consulta_sql, params, headers, conclusion_text, chart_labels
    ):
        datos = formatear_meses(DB.ejecutar_consulta(consulta_sql, params, fetch_all=True) or [])
        story.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
        story.append(Spacer(1, 10))

        if not datos:
            story.append(Paragraph("Sin datos disponibles", styles["Normal"]))
            story.append(PageBreak())
            return

        # ==== Tabla ====
        filas = [headers]
        for row in datos:
            fila = []
            for h in headers:
                key = (
                    h.lower()
                    .replace(" (%)", "")
                    .replace(" ($)", "")
                    .replace(" ", "_")
                )
                valor = row.get(key, 0)
                try:
                    fila.append(format_decimal(float(valor)))
                except:
                    fila.append(str(valor))
            filas.append(fila)

        tabla = Table(filas, hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6fff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 15))

        # ==== Gráfica ====
        try:
            meses = [row["mes"] for row in datos]
            valores = {}
            for label in chart_labels:
                serie = []
                for row in datos:
                    val = row.get(label.lower())
                    if val is None:
                        serie.append(0.0)
                    else:
                        try:
                            serie.append(float(val))
                        except ValueError:
                            serie.append(0.0)
                valores[label] = serie

            plt.figure(figsize=(6, 3))
            for label, serie in valores.items():
                plt.plot(meses, serie, marker="o", label=label)

            plt.title(titulo)
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            grafica = io.BytesIO()
            plt.savefig(grafica, format="png")
            plt.close()
            grafica.seek(0)
            story.append(Image(grafica, width=400, height=200))
            story.append(Spacer(1, 10))
        except Exception as e:
            story.append(Paragraph(f"⚠️ No se pudo generar gráfica: {e}", styles["Normal"]))

        # ==== Recomendación ====
        story.append(Paragraph(conclusion_text, styles["Normal"]))
        story.append(PageBreak())

    # ====== Consultas SQL ======
    agregar_reporte(
        "Estado de Resultados",
        """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS costos,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario) -
                     SUM(dc.cantidad * dc.precio_unitario), 0) AS utilidad
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
        """,
        (inicio_date, fin_date),
        ["Mes", "Ingresos", "Costos", "Utilidad"],
        "Muestra los ingresos, costos y utilidad por cada mes.",
        ["Ingresos", "Costos", "Utilidad"],
    )

    agregar_reporte(
        "Margen de Rentabilidad",
        """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            ROUND((
                COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) - 
                COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
            ) / NULLIF(COALESCE(SUM(dv.cantidad * dv.precio_unitario),0),0) * 100, 2) AS margen
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
        """,
        (inicio_date, fin_date),
        ["Mes", "Margen (%)"],
        "Evalúa la eficiencia de las ventas respecto a costos.",
        ["Margen"],
    )

    agregar_reporte(
        "Flujo de Caja",
        """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS egresos,
            COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) -
            COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS flujo
        FROM meses m
        LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
        LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
        GROUP BY m.mes
        ORDER BY m.mes;
        """,
        (inicio_date, fin_date),
        ["Mes", "Ingresos", "Egresos", "Flujo"],
        "Muestra entradas y salidas de efectivo mensuales.",
        ["Ingresos", "Egresos", "Flujo"],
    )

    agregar_reporte(
    "Punto de Equilibrio",
    """
    WITH meses AS (
        SELECT DATE_TRUNC('month', dd)::date AS mes
        FROM generate_series(%s, %s, interval '1 month') dd
    )
    SELECT 
        TO_CHAR(m.mes, 'YYYY-MM') AS mes,
        COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0) AS ingresos,
        COALESCE(SUM(dc.cantidad * dc.precio_unitario), 0) AS costos,
        CASE 
            WHEN COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) = 0 AND
                 COALESCE(SUM(dc.cantidad * dc.precio_unitario),0) = 0
                THEN 'N/A'
            WHEN COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) > 
                 COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
                THEN 'Utilidad'
            WHEN COALESCE(SUM(dv.cantidad * dv.precio_unitario),0) < 
                 COALESCE(SUM(dc.cantidad * dc.precio_unitario),0)
                THEN 'Pérdida'
            ELSE 'Equilibrio'
        END AS estado
    FROM meses m
    LEFT JOIN ventas v ON DATE_TRUNC('month', v.fecha) = m.mes
    LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
    LEFT JOIN detalle_compras dc ON dv.id_producto = dc.id_producto
    GROUP BY m.mes
    ORDER BY m.mes;
    """,
    (inicio_date, fin_date),
    ["Mes", "Ingresos", "Costos", "Estado"],
    "Indica si el mes tuvo Utilidad, Pérdida o Equilibrio.",
    ["Ingresos", "Costos"],
)


    agregar_reporte(
        "Crecimiento de Ventas",
        """
        WITH meses AS (
            SELECT DATE_TRUNC('month', dd)::date AS mes
            FROM generate_series(%s, %s, interval '1 month') dd
        ), ingresos AS (
            SELECT DATE_TRUNC('month', v.fecha)::date AS mes,
                   SUM(dv.cantidad * dv.precio_unitario) AS ingresos
            FROM ventas v
            JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
            WHERE v.fecha BETWEEN %s AND %s
            GROUP BY DATE_TRUNC('month', v.fecha)
        )
        SELECT 
            TO_CHAR(m.mes, 'YYYY-MM') AS mes,
            COALESCE(i.ingresos, 0) AS ingresos,
            ROUND((
                (COALESCE(i.ingresos,0) -
                 LAG(COALESCE(i.ingresos,0)) OVER (ORDER BY m.mes)) /
                 NULLIF(LAG(COALESCE(i.ingresos,0)) OVER (ORDER BY m.mes),0)
            ) * 100, 2) AS crecimiento
        FROM meses m
        LEFT JOIN ingresos i ON m.mes = i.mes
        ORDER BY m.mes;
        """,
        (inicio_date, fin_date, inicio_date, fin_date),
        ["Mes", "Ingresos", "Crecimiento (%)"],
        "Muestra la variación porcentual de ventas mes a mes.",
        ["Ingresos", "Crecimiento"],
    )

    # ====== Footer ======
    def add_footer(canvas, _doc):
        canvas.saveState()
        footer = (
            f"Tienda Julio y Mary | Generado el "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(A4[0] / 2.0, 15, footer)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        as_attachment=True,
        download_name=f"reporte_general_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    )
