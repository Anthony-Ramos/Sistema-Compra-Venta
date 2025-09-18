"""Controlador de autenticación para usuarios.
<<<<<<< HEAD

Este módulo define las rutas relacionadas con el inicio de sesión,
registro y menú principal utilizando Flask y Blueprints.
"""
import re
import psycopg2
from flask import session
from flask import make_response
from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.modelos.usuario_modelo import Usuario

# Blueprint para las rutas de autenticación
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Abre la sesión del usuario.
    """

=======

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
>>>>>>> practicas
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        user = Usuario.autenticar(usuario, contrasena)
        if user:
            session["usuario_id"] = user.id_usuario
            session["usuario_nombre"] = user.nom_usuario
<<<<<<< HEAD
            session["usuario_rol"] = Usuario.obtener_nombre_rol(user.id_rol)  # ⬅️ Nuevo
=======
            session["usuario_rol"] = Usuario.obtener_nombre_rol(user.id_rol)
>>>>>>> practicas

            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("auth.menu"))

        flash("Usuario o contraseña incorrectos", "danger")
<<<<<<< HEAD
        return render_template("auth/index.html")

    return render_template("auth/index.html")
@auth_bp.route("/logout")
def logout():
    """
    Cierra la sesión del usuario.
    """
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/registro", methods=["GET", "POST"])
=======
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
>>>>>>> practicas
def registro():
    """
    Muestra y procesa el formulario de registro de usuarios.
    """
    if request.method == "POST":
        nom_usuario = request.form.get("nom_usuario")
<<<<<<< HEAD
        contrasena  = request.form.get("contrasena")
        confirmar   = request.form.get("confirmar")
        id_rol      = request.form.get("id_rol")
=======
        contrasena = request.form.get("contrasena")
        confirmar = request.form.get("confirmar")
        id_rol = request.form.get("id_rol")
>>>>>>> practicas

        if not nom_usuario or not contrasena or not confirmar or not id_rol:
            flash("Complete todos los campos.", "warning")
        elif contrasena != confirmar:
            flash("Las contraseñas no coinciden.", "warning")
        elif (
<<<<<<< HEAD
            len(contrasena) < 8 or 
            not re.search(r"\d", contrasena) or 
            not re.search(r"[A-Z]", contrasena) or 
            not re.search(r"[a-z]", contrasena)
        ):
            flash("La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números.", "warning")
=======
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
>>>>>>> practicas
        else:
            try:
                nuevo_id = Usuario.registrar(nom_usuario, contrasena, int(id_rol))
                flash(f"Usuario creado con id {nuevo_id}", "success")
            except ValueError as e:
                flash(str(e), "warning")

<<<<<<< HEAD
    # 👇 Esta línea se ejecuta SIEMPRE
=======
>>>>>>> practicas
    usuarios = Usuario.obtener_todos()
    return render_template("auth/usuarios.html", usuarios=usuarios)


@auth_bp.route("/menu")
<<<<<<< HEAD
def menu():
    """
    Muestra y procesa el formulario de menús.
    """

    if "usuario_id" not in session:
        flash("Inicie sesión para continuar.", "warning")
        return redirect(url_for("auth.login"))
    response = make_response(render_template("auth/menu.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@auth_bp.route("/usuarios")
=======
@login_requerido
def menu():
    """
    Muestra el menú principal.
    """
    return render_template("auth/Menu.html")


@auth_bp.route("/usuarios")
@login_requerido
>>>>>>> practicas
def listar_usuarios():
    """
    Muestra una tabla con todos los usuarios registrados.
    """
<<<<<<< HEAD
    usuarios = Usuario.obtener_todos()  # Este método lo crearemos en el modelo
    return render_template("auth/tabla_usuarios.html", usuarios=usuarios)

@auth_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    """
    Actualiza el nombre y rol de un usuario por su ID.

    Si la petición es POST, guarda los cambios. 
    Si es GET, redirige al formulario de registro.
=======
    usuarios = Usuario.obtener_todos()
    return render_template("auth/tabla_usuarios.html", usuarios=usuarios)


@auth_bp.route('/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_requerido
def editar_usuario(id_usuario):
    """
    Actualiza el nombre y rol de un usuario por su ID.
>>>>>>> practicas
    """
    if request.method == 'POST':
        nom_usuario = request.form.get('nom_usuario')
        id_rol = request.form.get('id_rol')
        try:
            Usuario.actualizar_nombre_rol(id_usuario, nom_usuario, int(id_rol))
            flash(f"Usuario con ID {id_usuario} actualizado correctamente.", "success")
        except psycopg2.Error as error:
            flash(f"Error al actualizar en la base de datos: {error}", "danger")

<<<<<<< HEAD
        return redirect(url_for('auth.registro'))  # ✅ Esto evita que se quede en /editar/id

    return redirect(url_for('auth.registro'))  # ← Si alguien entra por GET, también redirige

@auth_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
=======
        return redirect(url_for('auth.registro'))

    return redirect(url_for('auth.registro'))


@auth_bp.route('/eliminar/<int:id_usuario>', methods=['POST'])
@login_requerido
>>>>>>> practicas
def eliminar_usuario(id_usuario):
    """
    Elimina un usuario de la base de datos según su ID.
    """
<<<<<<< HEAD
    Usuario.eliminar(id_usuario)  # Asumiendo que tenés este método en tu modelo
    flash(f"Usuario con ID {id_usuario} eliminado correctamente.", "success")
    return redirect(url_for('auth.registro'))  # o donde esté tu lista

@auth_bp.route('/productos')
def productos():
    "lleva a vista productos"
    return render_template('auth/productos.html')


# ENDPOINTS ADICIONALES PARA EL MENÚ

@auth_bp.route('/inventario')
def inventario():
    """Página de inventario"""
    return render_template('auth/inventario.html')

@auth_bp.route('/compras')
def compras():
    """Página de compras"""
    return render_template('auth/compras.html')

@auth_bp.route('/reportes')
def reportes():
    """Página de reportes"""
    return render_template('auth/reportes.html')

@auth_bp.route('/ventas')
def ventas():
    """Página de ventas"""
    return render_template('auth/ventas.html')

@auth_bp.route('/proveedor')
def proveedor():
    """Página de proveedor"""
    return render_template('auth/proveedor.html')

@auth_bp.route('/categoria')
def categoria():
    """Página de categorias"""
    return render_template('auth/categoria.html')

@auth_bp.route('/stockmin')
def stockmin():
    """Página de productos con stock bajo"""
    return render_template('auth/stockMin.html')

@auth_bp.route('/movi')
def movi():
    return render_template('auth/movi.html')
=======
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
>>>>>>> practicas
