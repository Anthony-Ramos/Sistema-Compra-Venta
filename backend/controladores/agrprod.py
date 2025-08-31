# pylint: disable=wrong-import-position
"""Módulo de API Flask para CRUD de productos.

Incluye endpoints para:
- Agregar producto
- Editar producto
- Eliminar producto
- Obtener categorías
- Obtener proveedores
- Listar productos
- Listar productos filtrados por categoría
"""

import os
import sys

# 👇 Ajustar sys.path antes de importar backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.db import DB
from backend.config import Config

# ===================== CONFIG APP ===================== #

app = Flask(__name__)

# Permitir CORS para todas las rutas (más simple en desarrollo)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500"]}})

# Inicializar pool de conexiones
DB.init_app(Config)


# ===================== ENDPOINTS ===================== #

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    """
    Inserta un nuevo producto en la base de datos.

    Request JSON:
    {
        "nombre": str,
        "descripcion": str,
        "categoria": int,
        "precio_compra": float,
        "precio_venta": float,
        "stock_minimo": int,
        "proveedor": int
    }

    Response:
        {"status": "ok"} o {"status": "error"}
    """
    data = request.get_json()
    print("Datos recibidos del formulario:", data)
    try:
        DB.execute(
            """
            INSERT INTO producto
                (nombre, descripcion, id_categoria, precio_compra,
                 precio_venta, stock_minimo, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data['nombre'],
                data['descripcion'],
                int(data['categoria']),
                float(data['precio_compra']),
                float(data['precio_venta']),
                int(data['stock_minimo']),
                int(data['proveedor'])
            )
        )
        return jsonify({"status": "ok"})
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al agregar producto:", e)
        return jsonify({"status": "error"}), 500


@app.route('/editar_producto/<int:id_producto>', methods=['PUT'])
def editar_producto(id_producto):
    """
    Edita un producto existente por su ID.

    Args:
        id_producto (int): ID del producto.

    Request JSON: igual que en agregar_producto.
    """
    data = request.get_json()
    print(f"Editando producto {id_producto} con datos:", data)
    try:
        DB.execute(
            """
            UPDATE producto
            SET nombre = %s,
                descripcion = %s,
                id_categoria = %s,
                precio_compra = %s,
                precio_venta = %s,
                stock_minimo = %s,
                id_proveedor = %s
            WHERE id_producto = %s
            """,
            (
                data['nombre'],
                data['descripcion'],
                int(data['categoria']),
                float(data['precio_compra']),
                float(data['precio_venta']),
                int(data['stock_minimo']),
                int(data['proveedor']),
                id_producto
            )
        )
        return jsonify({"status": "ok"})
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al editar producto:", e)
        return jsonify({"status": "error"}), 500


@app.route('/eliminar_producto/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    """
    Elimina un producto de la base de datos por su ID.
    """
    try:
        DB.execute("DELETE FROM producto WHERE id_producto = %s", (id_producto,))
        return jsonify({"status": "ok"})
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al eliminar producto:", e)
        return jsonify({"status": "error"}), 500


@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    """
    Obtiene todas las categorías de productos.

    Response:
        [
            {"id": int, "nombre": str},
            ...
        ]
    """
    try:
        categorias = DB.fetch_all(
            "SELECT id_categoria, nombre FROM categoria_producto ORDER BY nombre;"
        )
        return jsonify([{"id": c[0], "nombre": c[1].strip()} for c in categorias])
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al obtener categorías:", e)
        return jsonify({"status": "error"}), 500


@app.route('/proveedores', methods=['GET'])
def obtener_proveedores():
    """
    Obtiene todos los proveedores.
    """
    try:
        proveedores = DB.fetch_all(
            "SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre;"
        )
        return jsonify([{"id": p[0], "nombre": p[1].strip()} for p in proveedores])
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al obtener proveedores:", e)
        return jsonify({"status": "error"}), 500


@app.route('/productos', methods=['GET'])
def obtener_productos():
    """
    Obtiene todos los productos con su categoría y proveedor.
    """
    try:
        query = """
            SELECT 
                p.id_producto,
                p.nombre,
                p.id_categoria,
                c.nombre AS categoria,
                p.id_proveedor,
                COALESCE(pr.nombre, '-') AS proveedor,
                p.precio_compra,
                p.precio_venta,
                p.stock_minimo,
                p.descripcion
            FROM producto p
            INNER JOIN categoria_producto c ON p.id_categoria = c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            ORDER BY p.id_producto;
        """
        productos = DB.fetch_all(query)

        resultado = [
            {
                "id_producto": int(p[0]),
                "nombre": p[1],
                "id_categoria": int(p[2]),
                "categoria": p[3].strip(),
                "id_proveedor": int(p[4]) if p[4] else None,
                "proveedor": p[5].strip() if p[5] else "-",
                "precio_compra": float(p[6]),
                "precio_venta": float(p[7]),
                "stock_minimo": int(p[8]),
                "descripcion": p[9] if p[9] else ""
            }
            for p in productos
        ]
        return jsonify(resultado)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error al obtener productos:", e)
        return jsonify({"status": "error"}), 500


@app.route('/productos_filtro', methods=['GET'])
def obtener_productos_filtro():
    """
    Obtiene productos filtrados por categoría.

    Query params:
        categoria (int): id de categoría opcional.
    """
    filtro_categoria = request.args.get('categoria', default="", type=str)
    try:
        query = """
            SELECT 
                p.id_producto,
                p.nombre,
                p.id_categoria,
                c.nombre AS categoria,
                p.id_proveedor,
                COALESCE(pr.nombre, '-') AS proveedor,
                p.precio_compra,
                p.precio_venta,
                p.stock_minimo,
                p.descripcion
            FROM producto p
            INNER JOIN categoria_producto c ON p.id_categoria = c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        """
        params = ()
        if filtro_categoria:
            query += " WHERE c.id_categoria = %s"
            params = (filtro_categoria,)

        productos = DB.fetch_all(query, params)

        resultado = [
            {
                "id_producto": int(p[0]),
                "nombre": p[1],
                "id_categoria": int(p[2]),
                "categoria": p[3].strip(),
                "id_proveedor": int(p[4]) if p[4] else None,
                "proveedor": p[5].strip() if p[5] else "-",
                "precio_compra": float(p[6]),
                "precio_venta": float(p[7]),
                "stock_minimo": int(p[8]),
                "descripcion": p[9] if p[9] else ""
            }
            for p in productos
        ]
        return jsonify(resultado)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ Error en filtro de productos:", e)
        return jsonify({"status": "error"}), 500


# ===================== MAIN ===================== #
if __name__ == "__main__":
    # ⚠️ host="0.0.0.0" permite acceder desde localhost y 127.0.0.1
    app.run(debug=True, host="0.0.0.0", port=5000)
