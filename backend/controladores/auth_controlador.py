"""Controlador de autenticación para usuarios.

Define las rutas relacionadas con:
- Inicio de sesión
- Cierre de sesión
- Registro de usuarios
- Menú principal
- Gestión de usuarios
- Gestión de productos
"""

import re
import psycopg2
from flask import session, Blueprint, render_template, request, redirect, url_for, flash
from backend.modelos.usuario_modelo import Usuario
from backend.utils.decoradores import login_requerido

# Blueprint para las rutas de autenticación
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Maneja el inicio de sesión de los usuarios.
    """
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        user = Usuario.autenticar(usuario, contrasena)
        if user:
            session["usuario_id"] = user.id_usuario
            session["usuario_nombre"] = user.nom_usuario
            session["usuario_rol"] = Usuario.obtener_nombre_rol(user.id_rol)

            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("auth.menu"))

        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """
    Cierra la sesión del usuario.
    """
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/registro", methods=["GET", "POST"])
@login_requerido
def registro():
    """
    Muestra y procesa el formulario de registro de usuarios.
    """
    if request.method == "POST":
        nom_usuario = request.form.get("nom_usuario")
        contrasena = request.form.get("contrasena")
        confirmar = request.form.get("confirmar")
        id_rol = request.form.get("id_rol")

        if not nom_usuario or not contrasena or not confirmar or not id_rol:
            flash("Complete todos los campos.", "warning")
        elif contrasena != confirmar:
            flash("Las contraseñas no coinciden.", "warning")
        elif (
            len(contrasena) < 8
            or not re.search(r"\d", contrasena)
            or not re.search(r"[A-Z]", contrasena)
            or not re.search(r"[a-z]", contrasena)
        ):
            flash(
                "La contraseña debe tener al menos 8 caracteres, "
                "incluir mayúsculas, minúsculas y números.",
                "warning"
            )
        else:
            try:
                nuevo_id = Usuario.registrar(nom_usuario, contrasena, int(id_rol))
                flash(f"Usuario creado con id {nuevo_id}", "success")
            except ValueError as e:
                flash(str(e), "warning")

    usuarios = Usuario.obtener_todos()
    return render_template("auth/usuarios.html", usuarios=usuarios)


@auth_bp.route("/menu")
@login_requerido
def menu():
    """
    Muestra el menú principal.
    """
    return render_template("auth/Menu.html")


@auth_bp.route("/usuarios")
@login_requerido
def listar_usuarios():
    """
    Muestra una tabla con todos los usuarios registrados.
    """
    usuarios = Usuario.obtener_todos()
    return render_template("auth/tabla_usuarios.html", usuarios=usuarios)


@auth_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_requerido
def editar_usuario(id_usuario):
    """
    Actualiza el nombre y rol de un usuario por su ID.
    """
    if request.method == 'POST':
        nom_usuario = request.form.get('nom_usuario')
        id_rol = request.form.get('id_rol')
        try:
            Usuario.actualizar_nombre_rol(id_usuario, nom_usuario, int(id_rol))
            flash(f"Usuario con ID {id_usuario} actualizado correctamente.", "success")
        except psycopg2.Error as error:
            flash(f"Error al actualizar en la base de datos: {error}", "danger")

        return redirect(url_for('auth.registro'))

    return redirect(url_for('auth.registro'))


@auth_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
@login_requerido
def eliminar_usuario(id_usuario):
    """
    Elimina un usuario de la base de datos según su ID.
    """
    Usuario.eliminar(id_usuario)
    flash(f"Usuario con ID {id_usuario} eliminado correctamente.", "success")
    return redirect(url_for('auth.registro'))


@auth_bp.route('/productos')
@login_requerido
def productos():
    """
    Muestra la vista de gestión de productos.
    """
    return render_template('auth/productos.html')
