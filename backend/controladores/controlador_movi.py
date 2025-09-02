# backend/controladores/controlador_movi.py
"""Controlador para movimientos (compras + ventas) del mes actual."""
from flask import Blueprint, jsonify
from backend.modelos.modelo_movi import Movimiento

# Puedes nombrar el blueprint como "movimientos" para usar url_for('movimientos.obtener_movimientos')
movi_bp = Blueprint("movimientos", __name__, url_prefix="/api")

@movi_bp.route("/movimientos", methods=["GET"])
def obtener_movimientos():
    """
    Devuelve todos los movimientos (compras + ventas) del mes actual.
    Cada ítem contiene:
      tipo, fecha, id_producto, producto, cantidad,
      precio_unitario, total_linea, contraparte, id_movimiento
    """
    try:
        items = Movimiento.obtener_mes_actual()
        data = [{
            "tipo": m.tipo,
            "fecha": m.fecha,
            "id_producto": m.id_producto,
            "producto": m.producto,
            "cantidad": m.cantidad,
            "precio_unitario": m.precio_unitario,
            "total_linea": m.total_linea,
            "contraparte": m.contraparte,
            "id_movimiento": m.id_movimiento
        } for m in items]
        return jsonify(data)
    except Exception as e:
        print(f"Error en obtener_movimientos: {e}")
        return jsonify({"error": str(e)}), 500

# (Opcional) Resumen rápido del mes actual calculado en servidor.
@movi_bp.route("/movimientos/resumen", methods=["GET"])
def resumen_movimientos():
    """
    Devuelve totales del mes actual:
      total_general, total_compras, total_ventas, conteo
    """
    try:
        items = Movimiento.obtener_mes_actual()
        total_general = sum(m.total_linea for m in items)
        total_compras = sum(m.total_linea for m in items if m.tipo == "COMPRA")
        total_ventas  = sum(m.total_linea for m in items if m.tipo == "VENTA")
        return jsonify({
            "total_general": float(total_general),
            "total_compras": float(total_compras),
            "total_ventas":  float(total_ventas),
            "conteo":        len(items)
        })
    except Exception as e:
        print(f"Error en resumen_movimientos: {e}")
        return jsonify({"error": str(e)}), 500