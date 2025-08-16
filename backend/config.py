import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = int(os.getenv("PG_PORT", "5432"))
    PG_DB   = os.getenv("PG_DB", "mi_base")
    PG_USER = os.getenv("PG_USER", "mi_usuario")
    PG_PASS = os.getenv("PG_PASS", "mi_clave")
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta")