"""Punto de entrada principal de la aplicación Flask."""

from flask import Flask
from flask import Flask, render_template
from backend.controladores.categoria_controlador import categoria_bp
from backend.controladores.ventas_controlador import ventas_bp
from backend.controladores.stockMin_controlador import stockmin_bp
from backend.controladores.compras_controlador import compras_bp
from backend.controladores.controlador_movi import movi_bp
from backend.controladores.auth_controlador import auth_bp
from backend.controladores.prod_controlador import prod_bp
from backend.controladores.cate_controlador import cate_bp
from backend.controladores.prov_controlador import prov_bp
from backend.config import Config
from backend.db import DB
import os


def crear_app():
    """Crea e inicializa la aplicación Flask."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    print("¿Existe index.html?", os.path.exists("templates/auth/index.html"))
    DB.init_app(Config)
    print("✅ Conexión a la base de datos inicializada correctamente")

    #Ismael
    app.register_blueprint(auth_bp)
    #Pablo
    app.register_blueprint(prod_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(prov_bp)
    #Richard
    app.register_blueprint(ventas_bp) 
    app.register_blueprint(categoria_bp)
    app.register_blueprint(compras_bp) 
    app.register_blueprint(stockmin_bp)
    app.register_blueprint(movi_bp)

    
    @app.route("/")
    def index():
        return render_template("auth/index.html")
    return app


if __name__ == "__main__":
    aplicacion = crear_app()
    aplicacion.run(debug=True)
