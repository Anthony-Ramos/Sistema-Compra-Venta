from flask import Flask, request, jsonify
from ..backend.db import obtener_conexion, liberar_conexion

app = Flask(__name__)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.get_json()
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO productos (id,nombre, categoria, proveedor, precio_compra, precio_venta, stock_minimo, descripcion)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['nombre'], data['categoria'], data['proveedor'],
            data['precio_compra'], data['precio_venta'],
            data['stock_minimo'], data['descripcion']
        ))
        conn.commit()
        cursor.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500
    finally:
        liberar_conexion(conn)

if __name__ == "__main__":
    app.run(debug=True)