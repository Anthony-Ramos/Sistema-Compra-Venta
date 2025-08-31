#Controlador dedicado al manejo de agregar,editar y elimar productos usando flask,blueprint
import psycopg2
from flask import Blueprint, request, jsonify
from backend.db import liberar_conexion
from backend.db import obtener_conexion

prod_bp = Blueprint("productos", __name__, url_prefix="/productos")

# Guardar producto
@prod_bp.route('/agregar', methods=['POST'])
def agregar_producto():
    """
    Agrega un nuevo producto a la base de datos.
    """
    data = request.get_json()
    print("📦 Datos recibidos del formulario:", data)

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO producto (nombre, descripcion, id_categoria, precio_compra, precio_venta, stock_minimo, id_proveedor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['nombre'],
            data['descripcion'],
            int(data['categoria']),
            float(data['precio_compra']),
            float(data['precio_venta']),
            int(data['stock_minimo']),
            int(data['proveedor'])
        ))
        conn.commit()
        cursor.close()
        return jsonify({"status": "ok", "mensaje": "Producto agregado correctamente ✅"})
    except Exception as e:
        print("❌ Error en agregar_producto:", e)
        return jsonify({"status": "error", "mensaje": str(e)}), 500
    finally:
        liberar_conexion(conn)
#Cargar categorias en el combobox
@prod_bp.route('/categorias', methods=['GET'])
def obtener_categorias():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_categoria, nombre FROM categoria ORDER BY nombre")
        categorias = cursor.fetchall()  # [(1, "Bebidas"), (2, "Snacks"), ...]
        cursor.close()
        lista = [{"id": cat[0], "nombre": cat[1]} for cat in categorias]
        return jsonify(lista)
    except Exception as e:
        print("❌ Error al obtener categorías:", e)
        return jsonify([]), 500
    finally:
        liberar_conexion(conn)
