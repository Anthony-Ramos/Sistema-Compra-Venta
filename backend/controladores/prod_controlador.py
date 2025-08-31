# backend/controladores/prod_controlador.py
from flask import Blueprint, jsonify, request
from backend.db import DB

prod_bp = Blueprint("productos", __name__)

@prod_bp.route("/categorias", methods=["GET"])
def obtener_categorias():
    try:
        # Trae todas las categorías
        categorias = DB.fetch_all("SELECT id_categoria, nombre FROM categoria_producto ORDER BY nombre")
        lista = [{"id": cat[0], "nombre": cat[1]} for cat in categorias]
        return jsonify(lista)
    except Exception as e:
        print("Error cargando categorías:", e)
        return jsonify([]), 500
    
#Obtener los proveedores
@prod_bp.route("/proveedores", methods=["GET"])
def obtener_proveedores():
    try:
        # Trae todos los Proveedores
        proveedores = DB.fetch_all("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre")
        lista = [{"id": prov[0], "nombre": prov[1]} for prov in proveedores]
        return jsonify(lista)
    except Exception as e:
        print("Error cargando proveedores:", e)
        return jsonify([]), 500
    
#Extraer la informacion de la tabla productos en general
@prod_bp.route("/productos_filtro", methods=["GET"])
def obtener_productos():
    try:
        # Parámetros de filtro
        categoria_id = request.args.get("categoria", default=None, type=int)
        query = request.args.get("q", default=None, type=str)

        sql = """
            SELECT p.id_producto, p.nombre, c.nombre as categoria, pr.nombre as proveedor,
                   p.precio_compra, p.precio_venta, p.stock_minimo, p.descripcion,
                   c.id_categoria, pr.id_proveedor
            FROM producto p
            JOIN categoria_producto c ON p.id_categoria = c.id_categoria
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        """
        params = []
        filtros = []

        if categoria_id:
            filtros.append("p.id_categoria = %s")
            params.append(categoria_id)

        if query:
            filtros.append("(p.nombre ILIKE %s OR pr.nombre ILIKE %s OR c.nombre ILIKE %s)")
            busqueda = f"%{query}%"
            params.extend([busqueda, busqueda, busqueda])

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

        sql += " ORDER BY p.nombre"

        productos = DB.fetch_all(sql, params)
        lista = [
            {
                "id_producto": p[0],
                "nombre": p[1],
                "categoria": p[2],
                "proveedor": p[3],
                "precio_compra": float(p[4]),
                "precio_venta": float(p[5]),
                "stock_minimo": p[6],
                "descripcion": p[7],
                "id_categoria": p[8],
                "id_proveedor": p[9]
            }
            for p in productos
        ]
        return jsonify(lista)

    except Exception as e:
        print("Error cargando productos:", e)
        return jsonify([]), 500
