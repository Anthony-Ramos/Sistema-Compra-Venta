"""Controlador para el manejo de productos con stock bajo."""
from flask import Blueprint, jsonify
from backend.modelos.stockMin import StockMinimo

stockmin_bp = Blueprint("stockmin", __name__, url_prefix="/api")

@stockmin_bp.route("/stock_minimo", methods=["GET"])
def obtener_stock_minimo():
    """Devuelve todos los productos con stock menor o igual a 30 en formato JSON."""
    try:
        productos = StockMinimo.obtener_bajo_stock()
        data = [{
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "stock_minimo": p.stock_minimo
        } for p in productos]
        return jsonify(data)
    except Exception as e:
        print(f"❌ Error en obtener_stock_minimo: {e}")
        return jsonify({"error": str(e)}), 500