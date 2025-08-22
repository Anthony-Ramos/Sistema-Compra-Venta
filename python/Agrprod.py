from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db import obtener_conexion, liberar_conexion
app = Flask(__name__)
CORS(app)

#endpoint para guardar producto
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.get_json()
    print("Datos recibidos del formulario:", data)
    conn = obtener_conexion()

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO producto (nombre, descripcion, id_categoria, precio_compra, precio_venta, stock_minimo,id_proveedor)
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
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

#endpoint para editar producto
@app.route('/editar_producto/<int:id_producto>', methods=['PUT'])
def editar_producto(id_producto):
    data = request.get_json()
    print(f"Editando producto {id_producto} con datos:", data)
    
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = """
        UPDATE producto
        SET nombre = %s,
            descripcion = %s,
            id_categoria = %s,
            precio_compra = %s,
            precio_venta = %s,
            stock_minimo = %s,
            id_proveedor = %s
        WHERE id_producto = %s
        """
        cursor.execute(query, (
            data['nombre'],
            data['descripcion'],
            int(data['categoria']),
            float(data['precio_compra']),
            float(data['precio_venta']),
            int(data['stock_minimo']),
            int(data['proveedor']),
            id_producto
        ))
        conn.commit()
        cursor.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

#endpoint para eliminar producto
@app.route('/eliminar_producto/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM producto WHERE id_producto = %s"
        cursor.execute(query, (id_producto,))
        conn.commit()
        cursor.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error al eliminar producto:", e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

#endpoint para traer categorías
@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_categoria, nombre FROM categoria_producto ORDER BY nombre;")
        categorias = cursor.fetchall()
        cursor.close()

        return jsonify([
            {"id": cat[0], "nombre": cat[1].strip()}  # .strip() si usaste CHAR
            for cat in categorias
        ])
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

#endpoint para atraer categorias
@app.route('/proveedores', methods=['GET'])
def obtener_proveedores():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre;')
        proveedores = cursor.fetchall()
        cursor.close()

        return jsonify([
            {"id": prov[0], "nombre": prov[1].strip()}  # 👈 corregido: prov en lugar de cat
            for prov in proveedores
        ])
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

# Endpoint para traer productos y llenar la tabla
@app.route('/productos', methods=['GET'])
def obtener_productos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
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
        cursor.execute(query)
        productos = cursor.fetchall()
        cursor.close()

        # Convertir a JSON
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
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

@app.route('/productos_filtro', methods=['GET'])
def obtener_productos_filtro():
    filtro_categoria = request.args.get('categoria', default="", type=str)
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
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
        if filtro_categoria:
            query += " WHERE c.id_categoria = %s"
            cursor.execute(query, (filtro_categoria,))
        else:
            cursor.execute(query)

        productos = cursor.fetchall()
        cursor.close()

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
    finally:
        liberar_conexion(conn)
if __name__ == "__main__":
    app.run(debug=True)