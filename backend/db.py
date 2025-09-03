"""Módulo db: manejo de conexiones a PostgreSQL con pool y métodos de ayuda."""

from contextlib import contextmanager
from typing import Any, Iterable, Optional, Tuple, List
from psycopg2.pool import SimpleConnectionPool
from backend.config import Config


class DB:
    """Clase para manejar un pool de conexiones PostgreSQL y métodos de utilidad."""

    _pool: Optional[SimpleConnectionPool] = None

    # ---------------------------
    # Inicialización del pool
    # ---------------------------
    @classmethod
    def init_app(cls, cfg: Config, minconn: int = 1, maxconn: int = 10) -> None:
        """Inicializa el pool de conexiones si no existe."""
        if cls._pool is None:
            cls._pool = SimpleConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                host=cfg.PG_HOST,
                port=cfg.PG_PORT,
                dbname=cfg.PG_DB,
                user=cfg.PG_USER,
                password=cfg.PG_PASS,
                client_encoding="UTF8",
                connect_timeout=10,
                application_name="mi-app"
            )
            print("✅ Pool de conexiones PostgreSQL inicializado correctamente.")

    @classmethod
    def get_pool(cls) -> Optional[SimpleConnectionPool]:
        """Retorna el pool de conexiones."""
        return cls._pool

    # ---------------------------
    # Métodos de conexión
    # ---------------------------
    @classmethod
    def obtener_conexion(cls):
        if cls._pool is None:
            raise RuntimeError("DB.init_app(Config) no fue llamado.")
        return cls._pool.getconn()

    @classmethod
    def liberar_conexion(cls, conn):
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def connection(cls):
        """Context manager para (conn, cur) con commit/rollback automático."""
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

    # ---------------------------
    # Métodos de consulta
    # ---------------------------
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

            if fetch_one:
                fila = cur.fetchone()
                if fila:
                    columnas = [desc[0] for desc in cur.description]
                    return dict(zip(columnas, fila))
                return None

            return None


# Función de compatibilidad con código antiguo
def iniciar_pool():
    """Inicializa el pool y retorna el objeto del pool."""
    DB.init_app(Config)
    return DB.get_pool()