from flask import Blueprint, jsonify, request
from backend.db import DB

cate_bp = Blueprint("categoria", __name__)

@cate_bp.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        data = request.get_json()        
        nombre = data["nombre"].strip()  # eliminar espacios al inicio/final
        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        # Verificar si ya existe la categoría
        check_query = "SELECT id_categoria FROM categoria_producto WHERE LOWER(nombre) = LOWER(%s)"
        existe = DB.fetch_one(check_query, (nombre,))
        if existe:
            return jsonify({"status": "error", "mensaje": "La categoría ya existe"}), 400

        # Insertar si no existe
        query = "INSERT INTO categoria_producto(nombre) VALUES(%s)"
        DB.execute(query, (nombre,))

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error agregando categoria:", e)
        return jsonify({"status": "error", "mensaje": "Error interno del servidor"}), 500

@cate_bp.route("/categorias", methods=["GET"])
def listar_categorias():
    try:
        query = "SELECT id_categoria AS id, nombre FROM categoria_producto ORDER BY id_categoria"
        categorias = DB.fetch_all(query)  # devuelve lista de tuplas

        # Convertir a lista de diccionarios
        categorias_dict = [{"id": cat[0], "nombre": cat[1]} for cat in categorias]

        return jsonify(categorias_dict)
    except Exception as e:
        print("Error al obtener categorias:", e)
        return jsonify({"status": "error"}), 500
    
@cate_bp.route("/eliminar_categoria/<int:id_cate>", methods=["DELETE"])
def eliminar_categoria(id_cate):
    try:
        print("Intentando eliminar id:", id_cate)
        DB.execute("DELETE FROM categoria_producto WHERE id_categoria=%s", (id_cate,))
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error eliminando categoria:", e)
        return jsonify({"status": "error"}), 500

@cate_bp.route("/editar_categoria/<int:id_cate>", methods=["PUT"])
def editar_categoria(id_cate):
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        query = "UPDATE categoria_producto SET nombre=%s WHERE id_categoria=%s"
        DB.execute(query, (nombre, id_cate))

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error editando categoria:", e)
        return jsonify({"status": "error"}), 500
