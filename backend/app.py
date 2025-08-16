from flask import Flask
from controladores.auth_controlador import auth_bp
from config import Config
from db import iniciar_pool

def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    iniciar_pool()
    app.register_blueprint(auth_bp)
    return app

if __name__ == "__main__":
    app = crear_app()
    app.run(debug=True)