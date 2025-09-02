"""Controlador para el manejo de compras."""
from flask import Blueprint, jsonify
from backend.modelos.modelo_compras import Compra

compras_bp = Blueprint("compras", __name__, url_prefix="/api")

@compras_bp.route("/compras", methods=["GET"])
def obtener_compras():
    """Devuelve todas las compras en formato JSON."""
    try:
        compras = Compra.obtener_todas()
        data = [{
            "proveedor": c.proveedor,
            "fecha": c.fecha,
            "producto": c.producto,
            "cantidad": c.cantidad,
            "precio_unitario": c.precio_unitario,
            "estado": c.estado,
            "total": c.total
        } for c in compras]
        return jsonify(data)
    except Exception as e:
        print(f"Error en obtener_compras: {e}")
        return jsonify({"error": str(e)}), 500
