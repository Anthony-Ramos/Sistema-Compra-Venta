"""Punto de entrada principal de la aplicación Flask."""

from flask import Flask, redirect, url_for
from backend.config import Config
from backend.db import DB
from backend.controladores.auth_controlador import auth_bp
from backend.controladores.prod_controlador import prod_bp
from backend.controladores.cate_controlador import cate_bp
from backend.controladores.prov_controlador import prov_bp
from backend.controladores.reportes_controlador import reportes_bp
from backend.controladores.reportes_financieros_controlador import financieros_bp



def crear_app():
    """Crea e inicializa la aplicación Flask."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    DB.init_app(Config)
    print("✅ Conexión a la base de datos inicializada correctamente")

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(prod_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(prov_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(financieros_bp)

    # ------------------------------
    # Ruta raíz → redirige al login
    # ------------------------------
    @app.route("/")
    def raiz():
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    aplicacion = crear_app()
    aplicacion.run(debug=True)
