from flask import Blueprint, jsonify, request
import bcrypt
from backend.db import DB

usua_bp = Blueprint("usuarios", __name__)

#agregar usuario
@usua_bp.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        contrasena = data.get("contrasena", "").strip()
        confirmar = data.get("confirmar", "").strip()
        id_rol = data.get("id_rol")
        correo = data.get("correo", "").strip()
        telefono = data.get("telefono", "").strip()

        # Validaciones básicas
        if not nombre:
            return jsonify({"status": "error", "mensaje": "El nombre no puede estar vacío"}), 400
        if not contrasena or not confirmar:
            return jsonify({"status": "error", "mensaje": "La contraseña no puede estar vacía"}), 400
        if contrasena != confirmar:
            return jsonify({"status": "error", "mensaje": "Las contraseñas no coinciden"}), 400
        if not id_rol:
            return jsonify({"status": "error", "mensaje": "Debe seleccionar un rol"}), 400
        if not correo:
            return jsonify({"status": "error", "mensaje": "El correo no puede estar vacío"}), 400
        if not telefono:
            return jsonify({"status": "error", "mensaje": "El teléfono no puede estar vacío"}), 400

        # Validar que el nombre, correo y teléfono no existan ya
        existe_query = """
            SELECT id_usuario FROM usuarios
            WHERE LOWER(nom_usuario)=LOWER(%s) OR correo=%s OR telefono=%s
        """
        existe = DB.fetch_one(existe_query, (nombre, correo, telefono))
        if existe:
            return jsonify({"status": "error", "mensaje": "El usuario, correo o teléfono ya existen"}), 400

        # Hash de la contraseña
        contrasena_hash = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

        # Insertar nuevo usuario
        insert_query = """
            INSERT INTO usuarios(nom_usuario, contrasena, id_rol, correo, telefono)
            VALUES(%s, %s, %s, %s, %s)
        """
        DB.execute(insert_query, (nombre, contrasena_hash, id_rol, correo, telefono))

        return jsonify({"status": "ok", "mensaje": "Usuario agregado exitosamente"})
    except Exception as e:
        print("Error agregando usuario:", e)
        return jsonify({"status": "error", "mensaje": "Error interno del servidor"}), 500

#Obtener los Roles 
@usua_bp.route("/obtener_roles", methods=["GET"])
def obtener_roles():
    try:
        # Trae todos los roles
        roles = DB.fetch_all("SELECT id_rol, nom_rol, activo FROM rol ORDER BY nom_rol")
        lista = [{
            "id": rol[0], 
            "nombre": rol[1], 
            "activo": rol[2]
            } for rol in roles]
        return jsonify(lista)
    except Exception as e:
        print("Error cargando roles:", e)
        return jsonify([]), 500
    
@usua_bp.route("/obtener_usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        usuarios = DB.fetch_all("""
            SELECT u.id_usuario, u.nom_usuario, u.correo, u.telefono, u.id_rol, r.nom_rol, u.activo
            FROM usuarios u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.activo = TRUE
            ORDER BY u.nom_usuario
        """)       
        lista_usuarios = []
        for u in usuarios:
            lista_usuarios.append({
                "id_usuario": u[0],
                "nom_usuario": u[1],
                "correo": u[2],
                "telefono": u[3],
                "id_rol": u[4],
                "rol": u[5],
                "activo": u[6]
            })
        return jsonify(lista_usuarios),200
    except Exception as e:
        print("Error cargando usuarios:", e)
        return jsonify([]), 500
    
    
    
    
    
    
# Agregar rol
@usua_bp.route("/agregar_rol", methods=["POST"])
def agregar_rol():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    if not nombre: return jsonify({"status":"error","mensaje":"Nombre requerido"}),400
    DB.execute("INSERT INTO rol(nom_rol, activo) VALUES(%s, TRUE)", (nombre,))
    return jsonify({"status":"ok","mensaje":"Rol agregado exitosamente"})

# Editar rol
@usua_bp.route("/editar_rol/<int:id_rol>", methods=["PUT"])
def editar_rol(id_rol):
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    if not nombre: return jsonify({"status":"error","mensaje":"Nombre requerido"}),400
    DB.execute("UPDATE rol SET nom_rol=%s WHERE id_rol=%s", (nombre, id_rol))
    return jsonify({"status":"ok","mensaje":"Rol actualizado exitosamente"})

@usua_bp.route("/cambiar_estado_rol/<int:id_rol>", methods=["PUT"])
def cambiar_estado_rol(id_rol):
    # Verificar si hay usuarios con este rol
    usuarios = DB.fetch_one("SELECT COUNT(*) FROM usuarios WHERE id_rol=%s AND activo=1", (id_rol,))
    if usuarios and usuarios[0] > 0:
        return jsonify({"status":"error","mensaje":"No se puede dar de baja este rol porque tiene usuarios activos"}),400
    
    # Cambiar estado
    rol = DB.fetch_one("SELECT activo FROM rol WHERE id_rol=%s", (id_rol,))
    if not rol: return jsonify({"status":"error","mensaje":"Rol no encontrado"}),404
    nuevo_estado = not rol[0]
    DB.execute("UPDATE rol SET activo=%s WHERE id_rol=%s", (nuevo_estado, id_rol))
    return jsonify({"status":"ok","mensaje": "Rol activado" if nuevo_estado else "Rol desactivado"})