<<<<<<< HEAD
"""Controlador de productos: define endpoints para CRUD de productos, categorías y proveedores."""

=======
# backend/controladores/prod_controlador.py
>>>>>>> main
from flask import Blueprint, jsonify, request
from backend.db import DB

prod_bp = Blueprint("productos", __name__)

<<<<<<< HEAD

@prod_bp.route("/categorias", methods=["GET"])
def obtener_categorias():
    """Devuelve todas las categorías de productos en formato JSON."""
    try:
        categorias = DB.fetch_all(
            "SELECT id_categoria, nombre FROM categoria_producto ORDER BY nombre"
        )
        lista = [{"id": cat[0], "nombre": cat[1]} for cat in categorias]
        return jsonify(lista)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error cargando categorías:", e)
        return jsonify([]), 500


@prod_bp.route("/proveedores", methods=["GET"])
def obtener_proveedores():
    """Devuelve todos los proveedores en formato JSON."""
    try:
        proveedores = DB.fetch_all(
            "SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre"
        )
        lista = [{"id": prov[0], "nombre": prov[1]} for prov in proveedores]
        return jsonify(lista)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error cargando proveedores:", e)
        return jsonify([]), 500


@prod_bp.route("/productos_filtro", methods=["GET"])
def obtener_productos():
    """Devuelve lista de productos filtrados por categoría o búsqueda de texto."""
    try:
        categoria_id = request.args.get("categoria", default=None, type=int)
        query = request.args.get("q", default=None, type=str)

        sql = """
            SELECT p.id_producto, p.nombre, c.nombre AS categoria, pr.nombre AS proveedor,
=======
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
    
#Estraer la informacion de la tabla productos en general
@prod_bp.route("/productos_filtro", methods=["GET"])
def obtener_productos():
    try:
        # Opción de filtrar por categoría
        categoria_id = request.args.get("categoria", default=None, type=int)

        sql = """
            SELECT p.id_producto, p.nombre, c.nombre as categoria, pr.nombre as proveedor,
>>>>>>> main
                   p.precio_compra, p.precio_venta, p.stock_minimo, p.descripcion,
                   c.id_categoria, pr.id_proveedor
            FROM producto p
            JOIN categoria_producto c ON p.id_categoria = c.id_categoria
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        """
        params = []
<<<<<<< HEAD
        filtros = []

        if categoria_id:
            filtros.append("p.id_categoria = %s")
            params.append(categoria_id)

        if query:
            filtros.append(
                "(p.nombre ILIKE %s OR pr.nombre ILIKE %s OR c.nombre ILIKE %s)"
            )
            busqueda = f"%{query}%"
            params.extend([busqueda, busqueda, busqueda])

        if filtros:
            sql += " WHERE " + " AND ".join(filtros)

=======
        if categoria_id:
            sql += " WHERE p.id_categoria = %s"
            params.append(categoria_id)

>>>>>>> main
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
<<<<<<< HEAD
                "id_proveedor": p[9],
=======
                "id_proveedor": p[9]
>>>>>>> main
            }
            for p in productos
        ]
        return jsonify(lista)

<<<<<<< HEAD
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error cargando productos:", e)
        return jsonify([]), 500


@prod_bp.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    """Agrega un nuevo producto a la base de datos."""
=======
    except Exception as e:
        print("Error cargando productos:", e)
        return jsonify([]), 500

@prod_bp.route("/agregar_producto", methods=["POST"])
def agregar_producto():
>>>>>>> main
    try:
        data = request.get_json()
        print("Datos recibidos del formulario:", data)

        query = """
<<<<<<< HEAD
        INSERT INTO producto 
        (nombre, descripcion, id_categoria, precio_compra, precio_venta, stock_minimo, id_proveedor)
=======
        INSERT INTO producto (nombre, descripcion, id_categoria, precio_compra, precio_venta, stock_minimo, id_proveedor)
>>>>>>> main
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data["nombre"],
            data["descripcion"],
            int(data["categoria"]),
            float(data["precio_compra"]),
            float(data["precio_venta"]),
            int(data["stock_minimo"]),
<<<<<<< HEAD
            int(data["proveedor"]),
        )

        DB.execute(query, params)

        return jsonify({"status": "ok"})
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error agregando producto:", e)
        return jsonify({"status": "error"}), 500


@prod_bp.route("/eliminar_producto/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    """Elimina un producto por su ID."""
=======
            int(data["proveedor"])
        )

        # Usando el helper DB (ej. DB.execute)
        DB.execute(query, params)

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error agregando producto:", e)
        return jsonify({"status": "error"}), 500

@prod_bp.route("/eliminar_producto/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
>>>>>>> main
    try:
        print("ID de producto a eliminar:", id_producto)

        query = "DELETE FROM producto WHERE id_producto = %s"
        params = (id_producto,)

        filas_afectadas = DB.execute(query, params)

        if filas_afectadas > 0:
            return jsonify({"status": "ok"})
<<<<<<< HEAD
        return jsonify({"status": "error", "msg": "Producto no encontrado"}), 404

    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error eliminando producto:", e)
        return jsonify({"status": "error"}), 500


@prod_bp.route("/editar_producto/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
    """Edita los datos de un producto existente."""
=======
        else:
            return jsonify({"status": "error", "msg": "Producto no encontrado"}), 404

    except Exception as e:
        print("Error eliminando producto:", e)
        return jsonify({"status": "error"}), 500

@prod_bp.route("/editar_producto/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
>>>>>>> main
    try:
        data = request.get_json()
        query = """
            UPDATE producto
            SET nombre=%s, descripcion=%s, id_categoria=%s, precio_compra=%s,
                precio_venta=%s, stock_minimo=%s, id_proveedor=%s
            WHERE id_producto=%s
        """
        params = (
<<<<<<< HEAD
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
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("Error editando producto:", e)
        return jsonify({"status": "error"}), 500
=======
            data["nombre"], data["descripcion"], int(data["categoria"]),
            float(data["precio_compra"]), float(data["precio_venta"]),
            int(data["stock_minimo"]), int(data["proveedor"]), id_producto
        )
        DB.execute(query, params)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error editando producto:", e)
        return jsonify({"status": "error"}), 500


>>>>>>> main
