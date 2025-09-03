"""Punto de entrada principal de la aplicación Flask."""
import os
from flask import Flask, render_template
from backend.controladores.auth_controlador import auth_bp
from backend.controladores.prod_controlador import prod_bp
from backend.controladores.cate_controlador import cate_bp
from backend.controladores.prov_controlador import prov_bp

from backend.config import Config
from backend.db import DB
from backend.db import iniciar_pool


def crear_app():
    """Crea e inicializa la aplicación Flask."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    print("¿Existe index.html?", os.path.exists("templates/auth/index.html"))

    DB.init_app(Config)
    print("✅ Conexión a la base de datos inicializada correctamente")

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(prod_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(prov_bp)

    @app.route("/")
    def index():
        return render_template("auth/index.html")

    return app


if __name__ == "__main__":
    aplicacion = crear_app()
    aplicacion.run(debug=True)
