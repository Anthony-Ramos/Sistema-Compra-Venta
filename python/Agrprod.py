from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db import obtener_conexion, liberar_conexion
app = Flask(__name__)
CORS(app)

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


# 🔹 Nuevo endpoint para traer categorías
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
if __name__ == "__main__":
    app.run(debug=True)