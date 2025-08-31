from flask import Blueprint, jsonify, request
from backend.db import DB

prov_bp = Blueprint("proveedor", __name__)

# Agregar proveedor
@prov_bp.route("/agregar_proveedor", methods=["POST"])
def agregar_proveedor():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        telefono = data.get("telefono", "").strip()
        email = data.get("email", "").strip()
        direccion = data.get("direccion", "").strip()

        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        # Verificar si ya existe el proveedor con mismo nombre y teléfono
        check_query = """
            SELECT id_proveedor 
            FROM proveedores 
            WHERE LOWER(nombre)=LOWER(%s) AND telefono=%s
        """
        existe = DB.fetch_one(check_query, (nombre, telefono))
        if existe:
            return jsonify({"status": "error", "mensaje": "El proveedor ya existe"}), 400

        # Insertar nuevo proveedor
        query = """
            INSERT INTO proveedores(nombre, telefono, email, direccion)
            VALUES(%s, %s, %s, %s)
        """
        DB.execute(query, (nombre, telefono, email, direccion))

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error agregando proveedor:", e)
        return jsonify({"status": "error", "mensaje": "Error interno del servidor"}), 500


# Listar proveedores
@prov_bp.route("/list-proveedores", methods=["GET"])
def listar_proveedores():
    try:
        query = "SELECT id_proveedor, nombre, telefono, email, direccion FROM proveedores ORDER BY id_proveedor"
        proveedores = DB.fetch_all(query)

        # Convertir a lista de diccionarios
        proveedores_dict = [
            {
                "id": prov[0],
                "nombre": prov[1],
                "telefono": prov[2],
                "email": prov[3],
                "direccion": prov[4]
            } for prov in proveedores
        ]

        return jsonify(proveedores_dict)
    except Exception as e:
        print("Error al obtener proveedores:", e)
        return jsonify({"status": "error"}), 500


# Eliminar proveedor
@prov_bp.route("/eliminar_proveedor/<int:id_prov>", methods=["DELETE"])
def eliminar_proveedor(id_prov):
    try:
        DB.execute("DELETE FROM proveedores WHERE id_proveedor=%s", (id_prov,))
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error eliminando proveedor:", e)
        return jsonify({"status": "error"}), 500


# Editar proveedor
@prov_bp.route("/editar_proveedor/<int:id_prov>", methods=["PUT"])
def editar_proveedor(id_prov):
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        telefono = data.get("telefono", "").strip()
        email = data.get("email", "").strip()
        direccion = data.get("direccion", "").strip()

        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400

        query = """
            UPDATE proveedores 
            SET nombre=%s, telefono=%s, email=%s, direccion=%s 
            WHERE id_proveedor=%s
        """
        DB.execute(query, (nombre, telefono, email, direccion, id_prov))

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error editando proveedor:", e)
        return jsonify({"status": "error"}), 500