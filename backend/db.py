"""Módulo db: manejo de conexiones a PostgreSQL con un pool y métodos de ayuda."""

from contextlib import contextmanager
from typing import Any, Iterable, Optional, Tuple, List

from psycopg2.pool import SimpleConnectionPool
from backend.config import Config

class DB:
    """
    Clase para manejar un pool de conexiones PostgreSQL + métodos de ayuda.
    Uso:
        from db import DB
        DB.init_app(Config)  # se llama una vez al iniciar la app

        fila = DB.fetch_one("SELECT 1")
        filas = DB.fetch_all("SELECT * FROM usuarios WHERE estado = %s", (True,))
        DB.execute("INSERT INTO usuarios(usuario, contrasena) VALUES (%s, %s)", (u, p))
    """

    _pool: Optional[SimpleConnectionPool] = None

    @classmethod
    def init_app(cls, cfg: Config, minconn: int = 1, maxconn: int = 10) -> None:
        """Inicializa el pool con base en la Config."""
        if cls._pool is not None:
            return  # ya inicializado

        dsn = (
            f"host={cfg.PG_HOST} port={cfg.PG_PORT} dbname={cfg.PG_DB} "
            f"user={cfg.PG_USER} password={cfg.PG_PASS}"
        )
        cls._pool = SimpleConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=dsn,
            connect_timeout=10,
            application_name="mi-app",
        )

    @classmethod
    @contextmanager
    def connection(cls):
        """Context manager que entrega (conn, cur) y asegura commit/rollback."""
        if cls._pool is None:
            raise RuntimeError("DB.init_app(Config) no fue llamado.")

        conn = cls._pool.getconn()
        try:
            with conn.cursor() as cur:
                yield conn, cur
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls._pool.putconn(conn)

    # ---------- Métodos de ayuda ----------

    @classmethod
    def fetch_one(
        cls, sql: str, params: Optional[Iterable[Any]] = None
    ) -> Optional[Tuple[Any, ...]]:
        """Retorna una sola fila o None."""
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchone()

    @classmethod
    def fetch_all(
        cls, sql: str, params: Optional[Iterable[Any]] = None
    ) -> List[Tuple[Any, ...]]:
        """Retorna todas las filas (lista, puede ser vacía)."""
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchall()

    @classmethod
    def execute(cls, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """Ejecuta INSERT/UPDATE/DELETE. Devuelve número de filas afectadas."""
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.rowcount

    @classmethod
    def execute_returning(
        cls, sql: str, params: Optional[Iterable[Any]] = None
    ) -> Tuple[Any, ...]:
        """
        Ejecuta con RETURNING y devuelve la fila retornada.
        Ejemplo:
            DB.execute_returning(
                "INSERT INTO usuarios(usuario, contrasena) VALUES (%s,%s) RETURNING id",
                (u, p)
            )
        """
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
        """
        Ejecuta una consulta SQL.
        - fetch_all=True: retorna lista de diccionarios.
        - fetch_one=True: retorna un solo diccionario.
        - Ninguno: hace commit (INSERT/UPDATE/DELETE).
        """
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

            # Para operaciones que no retornan (ej. INSERT sin RETURNING)
            return None