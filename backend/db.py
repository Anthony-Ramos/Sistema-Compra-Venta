<<<<<<< Updated upstream
import psycopg2
from psycopg2 import pool
from .config import Config

_pool = None

def iniciar_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(
            1, 10,
            host=Config.PG_HOST,
            port=Config.PG_PORT,
            dbname=Config.PG_DB,
            user=Config.PG_USER,
            password=Config.PG_PASS,
            client_encoding='UTF8'
        )
        print("Conexion exitosa")
=======
"""db.py con configuración de locale para Windows"""

from contextlib import contextmanager
from typing import Any, Iterable, Optional, Tuple, List
import os
import locale
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from backend.config import Config
>>>>>>> Stashed changes

def obtener_conexion():
    if _pool is None:
        iniciar_pool()
    return _pool.getconn()

<<<<<<< Updated upstream
def liberar_conexion(conn):
    if _pool:
        _pool.putconn(conn)
=======
class DB:
    """
    Clase para manejar un pool de conexiones PostgreSQL y métodos de utilidad.
    """

    _pool: Optional[SimpleConnectionPool] = None

    @classmethod
    def init_app(cls, cfg: Config, minconn: int = 1, maxconn: int = 10) -> None:
        """
        Inicializa el pool de conexiones con configuración de locale para Windows.
        """
        if cls._pool is None:
            print("🔎 Debug conexión PostgreSQL:")
            print(f"HOST: {repr(cfg.PG_HOST)}")
            print(f"PORT: {repr(cfg.PG_PORT)}")
            print(f"DB: {repr(cfg.PG_DB)}")
            print(f"USER: {repr(cfg.PG_USER)}")
            print(f"PASS: {repr(cfg.PG_PASS)}")

            print(f"🌐 Locale actual: {locale.getlocale()}")
            print(f"🌐 Encoding preferido: {locale.getpreferredencoding()}")

            # Forzar variables de entorno
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["PGCLIENTENCODING"] = "UTF8"

            try:
                print("\n🔄 Intentando crear pool de conexiones...")

                cls._pool = SimpleConnectionPool(
                    minconn=minconn,
                    maxconn=maxconn,
                    host=cfg.PG_HOST,
                    port=cfg.PG_PORT,
                    database=cfg.PG_DB,
                    user=cfg.PG_USER,
                    password=cfg.PG_PASS,
                    connect_timeout=10,
                    application_name="mi-app"
                )

                # Test de conexión
                test_conn = cls._pool.getconn()
                try:
                    test_conn.set_client_encoding("UTF8")
                    with test_conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        print(f"🧪 Test básico: {cur.fetchone()}")

                        cur.execute("SHOW client_encoding")
                        print(f"📋 Encoding final: {cur.fetchone()[0]}")

                        cur.execute("SELECT 'Prueba áéíóú ñ'")
                        print(f"🔤 Test UTF-8: {cur.fetchone()[0]}")
                finally:
                    cls._pool.putconn(test_conn)

                print("✅ Pool de conexiones PostgreSQL inicializado correctamente.")

            except Exception as e:
                print(f"❌ Error creando pool: {e}")

                # Último intento: conexión directa sin pool
                print("\n🔄 Último intento: conexión directa sin pool...")
                try:
                    direct_conn = psycopg2.connect(
                        host=cfg.PG_HOST,
                        port=cfg.PG_PORT,
                        database=cfg.PG_DB,
                        user=cfg.PG_USER,
                        password=cfg.PG_PASS,
                    )
                    direct_conn.set_client_encoding("UTF8")

                    with direct_conn.cursor() as cur:
                        cur.execute("SELECT 'Conexión directa exitosa'")
                        print(f"✅ Conexión directa: {cur.fetchone()[0]}")

                    direct_conn.close()

                    # Crear un pool reducido como fallback
                    cls._pool = SimpleConnectionPool(
                        minconn=1,
                        maxconn=3,
                        host=cfg.PG_HOST,
                        port=cfg.PG_PORT,
                        database=cfg.PG_DB,
                        user=cfg.PG_USER,
                        password=cfg.PG_PASS,
                    )

                    print("✅ Pool creado como último recurso")

                except Exception as final_error:
                    print(f"❌ Error en último intento: {final_error}")
                    raise RuntimeError("No se pudo establecer conexión con PostgreSQL")

    @classmethod
    def obtener_conexion(cls):
        if cls._pool is None:
            raise RuntimeError("DB.init_app(Config) no fue llamado.")
        conn = cls._pool.getconn()

        # Forzar UTF-8 siempre en cada conexión
        try:
            conn.set_client_encoding("UTF8")
        except Exception as e:
            print(f"⚠️ No se pudo forzar UTF-8 en conexión: {e}")

        return conn

    @classmethod
    def liberar_conexion(cls, conn):
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def connection(cls):
        conn = cls.obtener_conexion()
        try:
            with conn.cursor() as cur:
                yield conn, cur
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.liberar_conexion(conn)

    @classmethod
    def fetch_one(cls, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[Tuple[Any, ...]]:
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchone()

    @classmethod
    def fetch_all(cls, sql: str, params: Optional[Iterable[Any]] = None) -> List[Tuple[Any, ...]]:
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchall()

    @classmethod
    def execute(cls, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.rowcount

    @classmethod
    def execute_returning(cls, sql: str, params: Optional[Iterable[Any]] = None) -> Tuple[Any, ...]:
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchone()

    @classmethod
    def ejecutar_consulta(
        cls,
        consulta: str,
        params: Optional[Iterable[Any]] = None,
        fetch_all: bool = False,
        fetch_one: bool = False
    ) -> Optional[Any]:
        with cls.connection() as (_, cur):
            cur.execute(consulta, params or ())

            if fetch_all:
                columnas = [desc[0] for desc in cur.description]
                return [dict(zip(columnas, fila)) for fila in cur.fetchall()]

            elif fetch_one:
                fila = cur.fetchone()
                if fila:
                    columnas = [desc[0] for desc in cur.description]
                    return dict(zip(columnas, fila))
                return None

            return None
>>>>>>> Stashed changes
