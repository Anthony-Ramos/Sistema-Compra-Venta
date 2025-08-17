from flask import Blueprint, render_template, request, redirect, url_for, flash

# Creamos un "Blueprint" para agrupar las rutas de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Ruta de Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        # Aquí iría la lógica real (consultar DB, validar contraseña, etc.)
        if usuario == "admin" and contrasena == "123456":
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('auth.menu'))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template('login.html')


# Ruta de Registro
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        # Aquí deberías guardar el usuario en PostgreSQL
        flash(f"Usuario {usuario} registrado correctamente", "success")
        return redirect(url_for('auth.login'))
    return render_template('registro.html')


# Ruta de Menú (ejemplo)
@auth_bp.route('/menu')
def menu():
    return render_template('menu.html')