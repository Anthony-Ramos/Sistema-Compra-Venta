# backend/controladores/categoria_controlador.py
from flask import Blueprint, jsonify, render_template
from backend.db import DB

categoria_bp = Blueprint("categorias", __name__, url_prefix="/api")

SQL_CATEGORIAS = """
SELECT
  c.id_categoria,
  c.nombre            AS nombre_categoria,
  COUNT(p.id_producto) AS total_productos
FROM categoria_producto AS c
LEFT JOIN producto AS p
  ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nombre
ORDER BY c.id_categoria;
"""

@categoria_bp.route("/categorias_grafica", methods=["GET"])
def categorias_grafica():
    try:
        rows = DB.ejecutar_consulta(SQL_CATEGORIAS, fetch_all=True) or []
        labels = [r["nombre_categoria"] for r in rows]
        values = [int(r["total_productos"]) for r in rows]
        ids = [r["id_categoria"] for r in rows]

        return jsonify({"ids": ids, "labels": labels, "values": values})
    except Exception as e:
        print("❌ Error en categorias_grafica:", e)
        return jsonify({"error": str(e)}), 500

# 👇 NUEVA RUTA PARA RENDERIZAR LA PÁGINA
@categoria_bp.route("/vista/categorias")
def vista_categorias():
    # Renderiza templates/categoriaGrafi.html
    return render_template("categoriaGrafi.html")