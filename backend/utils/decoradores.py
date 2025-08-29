"""Módulo de decoradores para proteger vistas en Flask.

Contiene el decorador login_requerido, que obliga a iniciar sesión
y añade cabeceras anti-caché a las respuestas protegidas.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, make_response

def login_requerido(view_func):
    """
    Decorador que protege las vistas que requieren autenticación.

    - Verifica si existe "usuario_id" en la sesión de Flask.
    - Si no hay sesión activa, redirige al login con un mensaje de advertencia.
    - Si hay sesión activa, ejecuta la vista y añade cabeceras HTTP para
      deshabilitar la caché del navegador. Esto evita que un usuario
      pueda regresar con el botón 'Atrás' tras cerrar sesión.

    Args:
        view_func (function): La función de vista de Flask que se quiere proteger.

    Returns:
        function: Una función wrapper que envuelve la vista original y
                  aplica las validaciones de sesión y cabeceras anti-caché.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicie sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))

        # Ejecuta la vista original
        response = make_response(view_func(*args, **kwargs))

        # Cabeceras anti-caché
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
    return wrapper
