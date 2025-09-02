"""Controlador para el manejo de ventas."""

from flask import Blueprint, jsonify, request
from backend.modelos.modelo_ventas import Venta

# Crear el blueprint para ventas
ventas_bp = Blueprint('ventas', __name__, url_prefix='/api')



@ventas_bp.route('/ventas/total', methods=['GET'])
def total_ventas():
    """
    Devuelve total general o total por mes:
    - /api/ventas/total            -> {"total": 123.45}
    - /api/ventas/total?mes=2025-08 -> {"total": 99.99}
    """
    try:
        mes = request.args.get('mes', type=str)
        total = Venta.total_por_mes(mes) if mes else Venta.total_todas()
        return jsonify({'total': total})
    except Exception as e:
        print(f"Error en total_ventas: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@ventas_bp.route('/ventas', methods=['GET'])
def obtener_ventas():
    """Endpoint para obtener todas las ventas."""
    try:
        ventas = Venta.obtener_todas()
        # Convertir los objetos Venta a diccionarios para JSON
        ventas_dict = []
        for venta in ventas:
            ventas_dict.append({
                'id_venta': venta.id_venta,
                'fecha': venta.fecha,
                'usuario': venta.usuario,
                'producto': venta.producto,
                'cantidad': venta.cantidad,
                'precio_unitario': venta.precio_unitario,
                'subtotal': venta.subtotal,
                'total_venta': venta.total_venta,
                'metodo_pago': venta.metodo_pago
            })
        return jsonify(ventas_dict)
    except Exception as e:
        print(f"Error en obtener_ventas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ventas_bp.route('/ventas/<int:id_venta>', methods=['GET'])
def obtener_venta_por_id(id_venta):
    """Endpoint para obtener una venta específica."""
    try:
        venta = Venta.buscar_por_id(id_venta)
        if venta:
            return jsonify({
                'id_venta': venta.id_venta,
                'fecha': venta.fecha,
                'usuario': venta.usuario,
                'producto': venta.producto,
                'cantidad': venta.cantidad,
                'precio_unitario': venta.precio_unitario,
                'subtotal': venta.subtotal,
                'total_venta': venta.total_venta,
                'metodo_pago': venta.metodo_pago
            })
        else:
            return jsonify({'error': 'Venta no encontrada'}), 404
    except Exception as e:
        print(f"Error en obtener_venta_por_id: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ventas_bp.route('/ventas/<int:id_venta>', methods=['DELETE'])
def eliminar_venta(id_venta):
    """Endpoint para eliminar una venta."""
    try:
        # Primero verificar que la venta existe
        venta = Venta.buscar_por_id(id_venta)
        if not venta:
            return jsonify({'error': 'Venta no encontrada'}), 404
        
        # Eliminar la venta
        Venta.eliminar(id_venta)
        return jsonify({'mensaje': 'Venta eliminada correctamente'}), 200
    except Exception as e:
        print(f"Error en eliminar_venta: {str(e)}")
        return jsonify({'error': str(e)}), 500