from flask import Blueprint, jsonify, request
from backend.modelos.cate_modelo import Categoria

cate_bp = Blueprint("categoria", __name__)

@cate_bp.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        data = request.get_json()
        nombre = data["nombre"].strip()
        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        Categoria.agregar(nombre)
        return jsonify({"status": "ok"})
    except ValueError as ve:
        return jsonify({"status": "error", "mensaje": str(ve)}), 400
    except Exception as e:
        print("Error agregando categoria:", e)
        return jsonify({"status": "error", "mensaje": "Error interno del servidor"}), 500

@cate_bp.route("/categorias", methods=["GET"])
def listar_categorias():
    try:
        categorias = Categoria.listar()
        return jsonify(categorias)
    except Exception as e:
        print("Error al obtener categorias:", e)
        return jsonify({"status": "error"}), 500

@cate_bp.route("/eliminar_categoria/<int:id_cate>", methods=["DELETE"])
def eliminar_categoria(id_cate):
    try:
        Categoria.eliminar(id_cate)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error eliminando categoria:", e)
        return jsonify({"status": "error"}), 500

@cate_bp.route("/editar_categoria/<int:id_cate>", methods=["PUT"])
def editar_categoria(id_cate):
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        Categoria.editar(id_cate, nombre)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error editando categoria:", e)
        return jsonify({"status": "error"}), 500