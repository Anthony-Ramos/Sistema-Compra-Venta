"""Punto de entrada principal de la aplicación Flask."""
import os
from flask import Flask, render_template<<<<<<< HEAD
from controladores.auth_controlador import auth_bp
from .config import Config
from db import iniciar_pool
=======
from flask import Flask, render_template
from backend.controladores.auth_controlador import auth_bp
from backend.config import Config
from backend.db import DB


def crear_app():
    """Crea e inicializa la aplicación Flask."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    DB.init_app(Config)
    print("✅ Conexión a la base de datos inicializada correctamente")

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    return app


if __name__ == "__main__":
    aplicacion = crear_app()
    aplicacion.run(debug=True)
