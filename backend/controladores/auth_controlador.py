"""Controlador de autenticación para usuarios.

Este módulo define las rutas relacionadas con el inicio de sesión,
registro y menú principal utilizando Flask y Blueprints.
"""
import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.modelos.usuario_modelo import Usuario

# Blueprint para las rutas de autenticación
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Muestra y procesa el formulario de inicio de sesión.

    Si la petición es POST, valida las credenciales y redirige al menú.
    Si falla, muestra un mensaje de error.
    """
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        user = Usuario.autenticar(usuario, contrasena)
        if user:
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("auth.menu"))

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("auth/Index.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """
    Muestra y procesa el formulario de registro de usuarios.
    """

    if request.method == "POST":
        nom_usuario = request.form.get("nom_usuario")
        contrasena  = request.form.get("contrasena")
        confirmar   = request.form.get("confirmar")
        id_rol      = request.form.get("id_rol")

        if not nom_usuario or not contrasena or not confirmar or not id_rol:
            flash("Complete todos los campos.", "warning")
        elif contrasena != confirmar:
            flash("Las contraseñas no coinciden.", "warning")
        else:
            try:
                nuevo_id = Usuario.registrar(nom_usuario, contrasena, int(id_rol))
                flash(f"Usuario creado con id {nuevo_id}", "success")
            except ValueError as e:
                flash(str(e), "warning")

    # 👇 Esta línea se ejecuta SIEMPRE
    usuarios = Usuario.obtener_todos()

    return render_template("auth/usuarios.html", usuarios=usuarios)


@auth_bp.route("/menu")
def menu():
    """
    Muestra el menú principal de la aplicación después del login.
    """
    return render_template("auth/Menu.html")

@auth_bp.route("/usuarios")
def listar_usuarios():
    """
    Muestra una tabla con todos los usuarios registrados.
    """
    usuarios = Usuario.obtener_todos()  # Este método lo crearemos en el modelo
    return render_template("auth/tabla_usuarios.html", usuarios=usuarios)

@auth_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    """
    Actualiza el nombre y rol de un usuario por su ID.

    Si la petición es POST, guarda los cambios. 
    Si es GET, redirige al formulario de registro.
    """
    if request.method == 'POST':
        nom_usuario = request.form.get('nom_usuario')
        id_rol = request.form.get('id_rol')
        try:
            Usuario.actualizar_nombre_rol(id_usuario, nom_usuario, int(id_rol))
            flash(f"Usuario con ID {id_usuario} actualizado correctamente.", "success")
        except psycopg2.Error as error:
            flash(f"Error al actualizar en la base de datos: {error}", "danger")

        return redirect(url_for('auth.registro'))  # ✅ Esto evita que se quede en /editar/id

    return redirect(url_for('auth.registro'))  # ← Si alguien entra por GET, también redirige

@auth_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    """
    Elimina un usuario de la base de datos según su ID.
    """
    Usuario.eliminar(id_usuario)  # Asumiendo que tenés este método en tu modelo
    flash(f"Usuario con ID {id_usuario} eliminado correctamente.", "success")
    return redirect(url_for('auth.registro'))  # o donde esté tu lista

@auth_bp.route('/productos')
def productos():
    "lleva a vista productos"
    return render_template('auth/productos.html')
