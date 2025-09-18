"""Controlador de productos: CRUD de productos, categorías y proveedores."""

# === Librerías estándar ===
import psycopg2

# === Librerías de terceros ===
from flask import Blueprint, jsonify, request

# === Módulos internos ===
from backend.db import DB

# =========================================
# Blueprint de productos con prefijo
# =========================================
prod_bp = Blueprint("productos", __name__, url_prefix="/productos")


# =======================
# Categorías
# =======================
@prod_bp.route("/categorias", methods=["GET"])
def obtener_categorias():
    """Devuelve todas las categorías de productos."""
    try:
        categorias = DB.fetch_all(
            "SELECT id_categoria, nombre FROM categoria_producto ORDER BY nombre"
        )
        lista = [{"id": cat[0], "nombre": cat[1]} for cat in categorias]
        return jsonify(lista)
    except psycopg2.Error as e:
        print("Error cargando categorías:", e)
        return jsonify([]), 500


# =======================
# Proveedores
# =======================
@prod_bp.route("/proveedores", methods=["GET"])
def obtener_proveedores():
    """Devuelve todos los proveedores."""
    try:
        proveedores = DB.fetch_all(
            "SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre"
        )
        lista = [{"id": prov[0], "nombre": prov[1]} for prov in proveedores]
        return jsonify(lista)
    except psycopg2.Error as e:
        print("Error cargando proveedores:", e)
        return jsonify([]), 500


# =======================
# Productos
# =======================
@prod_bp.route("/productos_filtro", methods=["GET"])
def obtener_productos():
    """Devuelve todos los productos, opcionalmente filtrados por categoría o nombre."""
    try:
        categoria_id = request.args.get("categoria", default=None, type=int)
        nombre = request.args.get("nombre", default=None, type=str)

        sql = """
            SELECT p.id_producto, p.nombre, c.nombre as categoria, pr.nombre as proveedor,
                   p.precio_compra, p.precio_venta, p.stock_minimo, p.descripcion,
                   c.id_categoria, pr.id_proveedor
            FROM producto p
            JOIN categoria_producto c ON p.id_categoria = c.id_categoria
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE 1=1
        """
        params = []

        # Filtro por categoría
        if categoria_id:
            sql += " AND p.id_categoria = %s"
            params.append(categoria_id)

        # Filtro por nombre (LIKE insensible a mayúsculas)
        if nombre:
            sql += " AND p.nombre ILIKE %s"
            params.append(f"%{nombre}%")

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
                "id_proveedor": p[9],
            }
            for p in productos
        ]
        return jsonify(lista)
    except psycopg2.Error as e:
        print("Error cargando productos:", e)
        return jsonify([]), 500



@prod_bp.route("/agregar", methods=["POST"])
def agregar_producto():
    """Inserta un nuevo producto en la base de datos."""
    try:
        data = request.get_json()
        print("Datos recibidos del formulario:", data)

        query = """
        INSERT INTO producto (nombre, descripcion, id_categoria, precio_compra,
                              precio_venta, stock_minimo, id_proveedor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data["nombre"],
            data["descripcion"],
            int(data["categoria"]),
            float(data["precio_compra"]),
            float(data["precio_venta"]),
            int(data["stock_minimo"]),
            int(data["proveedor"]),
        )

        DB.execute(query, params)
        return jsonify({"status": "ok"})
    except psycopg2.Error as e:
        print("Error agregando producto:", e)
        return jsonify({"status": "error"}), 500


@prod_bp.route("/eliminar/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    """Elimina un producto por su ID."""
    try:
        print("ID de producto a eliminar:", id_producto)
        query = "DELETE FROM producto WHERE id_producto = %s"
        filas_afectadas = DB.execute(query, (id_producto,))

        if filas_afectadas > 0:
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "msg": "Producto no encontrado"}), 404

    except psycopg2.Error as e:
        print("Error eliminando producto:", e)
        return jsonify({"status": "error"}), 500


@prod_bp.route("/editar/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
    """Actualiza un producto existente."""
    try:
        data = request.get_json()
        query = """
            UPDATE producto
            SET nombre=%s, descripcion=%s, id_categoria=%s, precio_compra=%s,
                precio_venta=%s, stock_minimo=%s, id_proveedor=%s
            WHERE id_producto=%s
        """
        params = (
            data["nombre"],
            data["descripcion"],
            int(data["categoria"]),
            float(data["precio_compra"]),
            float(data["precio_venta"]),
            int(data["stock_minimo"]),
            int(data["proveedor"]),
            id_producto,
        )
        DB.execute(query, params)
        return jsonify({"status": "ok"})
    except psycopg2.Error as e:
        print("Error editando producto:", e)
        return jsonify({"status": "error"}), 500
    
@prod_bp.route("/bajo_stock", methods=["GET"])
def productos_bajo_stock():
    """Devuelve productos agotados o con stock bajo."""
    try:
        sql = """
            SELECT id_producto, nombre, stock_actual, stock_minimo
            FROM producto
            WHERE stock_actual <= stock_minimo
            ORDER BY nombre
        """
        productos = DB.fetch_all(sql)
        lista = [
            {
                "id_producto": p[0],
                "nombre": p[1],
                "stock_actual": p[2],
                "stock_minimo": p[3],
                "agotado": p[2] == 0   # 🔹 Campo adicional para saber si está agotado
            }
            for p in productos
        ]
        return jsonify(lista)
    except psycopg2.Error as e:
        print("Error obteniendo productos bajo stock:", e)
        return jsonify([]), 500
