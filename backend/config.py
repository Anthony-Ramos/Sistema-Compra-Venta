import os
from dotenv import load_dotenv
<<<<<<< Updated upstream
load_dotenv()
=======

# Carga variables desde .env con encoding UTF-8 explícito
load_dotenv(encoding='utf-8')
>>>>>>> Stashed changes

class Config:
<<<<<<< Updated upstream
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = int(os.getenv("PG_PORT", "5433"))
    PG_DB   = os.getenv("PG_DB", "BDTJM")
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASS = os.getenv("PG_PASS", "root")
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta")
=======
    """Carga variables de entorno (con valores por defecto razonables)."""

    # App
    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "1") == "1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")

    # Base de datos (PostgreSQL)
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    PG_PORT: int = int(os.getenv("PG_PORT", "5433"))  # 5432 es el default de Postgres
    PG_DB: str = os.getenv("PG_DB",  "DBTJM")
    PG_USER: str = os.getenv("PG_USER", "postgres")
    PG_PASS: str = os.getenv("PG_PASS", "root")

    @classmethod
    def dsn(cls) -> str:
        """Devuelve el DSN listo para psycopg2 / pools con encoding UTF-8."""
        return (
            f"host={cls.PG_HOST} port={cls.PG_PORT} dbname={cls.PG_DB} "
            f"user={cls.PG_USER} password={cls.PG_PASS} client_encoding=utf8"
        )

    @classmethod
    def url(cls) -> str:
        """Devuelve URL estilo SQLAlchemy (por si más adelante migras)."""
        return f"postgresql://{cls.PG_USER}:{cls.PG_PASS}@{cls.PG_HOST}:{cls.PG_PORT}/{cls.PG_DB}?client_encoding=utf8"

    @classmethod
    def get_db_params(cls) -> dict:
        """Devuelve parámetros de BD como diccionario para SimpleConnectionPool."""
        return {
            'host': cls.PG_HOST,
            'port': cls.PG_PORT,
            'database': cls.PG_DB,
            'user': cls.PG_USER,
            'password': cls.PG_PASS,
            'client_encoding': 'utf8',
            'options': '-c client_encoding=utf8'
        }
>>>>>>> Stashed changes
