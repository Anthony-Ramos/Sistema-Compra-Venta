import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = int(os.getenv("PG_PORT", "5433"))
    PG_DB   = os.getenv("PG_DB", "BDTJM")
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASS = os.getenv("PG_PASS", "root")
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta")