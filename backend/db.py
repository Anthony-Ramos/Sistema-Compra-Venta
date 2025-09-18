"""Módulo db: manejo de conexiones a PostgreSQL con un pool y métodos de ayuda."""

from contextlib import contextmanager
from typing import Any, Iterable, Optional, Tuple, List

from psycopg2.pool import SimpleConnectionPool
from backend.config import Config
<<<<<<< HEAD

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
=======


class DB:
    """
    Clase para manejar un pool de conexiones PostgreSQL y métodos de utilidad.

    Ejemplo de uso:
        DB.init_app(Config)  # Se llama una vez al iniciar la aplicación

        conn = DB.obtener_conexion()
        DB.liberar_conexion(conn)

        # Consultas útiles
        fila = DB.fetch_one("SELECT 1")
        filas = DB.fetch_all("SELECT * FROM usuarios WHERE estado = %s", (True,))
        DB.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    """

    _pool: Optional[SimpleConnectionPool] = None

    @classmethod
    def init_app(cls, cfg: Config, minconn: int = 1, maxconn: int = 10) -> None:
        """
        Inicializa el pool de conexiones si aún no ha sido creado.

        Parámetros:
            cfg (Config): Objeto de configuración con credenciales de la base de datos.
            minconn (int): Número mínimo de conexiones en el pool.
            maxconn (int): Número máximo de conexiones en el pool.
        """
        if cls._pool is None:
            cls._pool = SimpleConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                host=cfg.PG_HOST,
                port=cfg.PG_PORT,
                dbname=cfg.PG_DB,
                user=cfg.PG_USER,
                password=cfg.PG_PASS,
                client_encoding='UTF8',
                connect_timeout=10,
                application_name="mi-app"
            )
            print("✅ Pool de conexiones PostgreSQL inicializado correctamente.")

    @classmethod
    def obtener_conexion(cls):
        """
        Obtiene una conexión desde el pool.

        Retorna:
            conexión activa (psycopg2.extensions.connection)

        Lanza:
            RuntimeError: si el pool no ha sido inicializado previamente.
        """
        if cls._pool is None:
            raise RuntimeError("DB.init_app(Config) no fue llamado.")
        return cls._pool.getconn()

    @classmethod
    def liberar_conexion(cls, conn):
        """
        Devuelve una conexión al pool.

        Parámetros:
            conn: conexión a devolver al pool.
        """
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def connection(cls):
        """
        Context manager que proporciona (conn, cur) para ejecutar SQL
        y asegura el manejo de commit/rollback automáticamente.

        Uso:
            with DB.connection() as (conn, cur):
                cur.execute("SELECT * FROM tabla")
        """
        conn = cls.obtener_conexion()
>>>>>>> practicas
        try:
            with conn.cursor() as cur:
                yield conn, cur
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
<<<<<<< HEAD
            cls._pool.putconn(conn)

    # ---------- Métodos de ayuda ----------

    @classmethod
    def fetch_one(
        cls, sql: str, params: Optional[Iterable[Any]] = None
    ) -> Optional[Tuple[Any, ...]]:
        """Retorna una sola fila o None."""
=======
            cls.liberar_conexion(conn)

    @classmethod
    def fetch_one(
    cls,
    sql: str,
    params: Optional[Iterable[Any]] = None
    ) -> Optional[Tuple[Any, ...]]:
        """
        Ejecuta una consulta SQL y devuelve una sola fila.

        Parámetros:
            sql (str): sentencia SQL a ejecutar.
            params (Iterable): parámetros opcionales.

        Retorna:
            Una tupla con los datos de la fila o None.
        """
>>>>>>> practicas
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchone()

    @classmethod
<<<<<<< HEAD
    def fetch_all(
        cls, sql: str, params: Optional[Iterable[Any]] = None
    ) -> List[Tuple[Any, ...]]:
        """Retorna todas las filas (lista, puede ser vacía)."""
=======
    def fetch_all(cls, sql: str, params: Optional[Iterable[Any]] = None) -> List[Tuple[Any, ...]]:
        """
        Ejecuta una consulta SQL y devuelve todas las filas.

        Parámetros:
            sql (str): sentencia SQL a ejecutar.
            params (Iterable): parámetros opcionales.

        Retorna:
            Lista de tuplas con los datos obtenidos.
        """
>>>>>>> practicas
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.fetchall()

    @classmethod
    def execute(cls, sql: str, params: Optional[Iterable[Any]] = None) -> int:
<<<<<<< HEAD
        """Ejecuta INSERT/UPDATE/DELETE. Devuelve número de filas afectadas."""
=======
        """
        Ejecuta una sentencia INSERT, UPDATE o DELETE.

        Parámetros:
            sql (str): consulta SQL.
            params (Iterable): parámetros opcionales.

        Retorna:
            int: número de filas afectadas.
        """
>>>>>>> practicas
        with cls.connection() as (_, cur):
            cur.execute(sql, params or ())
            return cur.rowcount

    @classmethod
<<<<<<< HEAD
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
=======
    def execute_returning(cls, sql: str, params: Optional[Iterable[Any]] = None) -> Tuple[Any, ...]:
        """
        Ejecuta una sentencia SQL con cláusula RETURNING y devuelve la fila retornada.

        Parámetros:
            sql (str): consulta SQL con RETURNING.
            params (Iterable): parámetros opcionales.

        Retorna:
            Tupla con los valores retornados.
>>>>>>> practicas
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
<<<<<<< HEAD
        Ejecuta una consulta SQL.
        - fetch_all=True: retorna lista de diccionarios.
        - fetch_one=True: retorna un solo diccionario.
        - Ninguno: hace commit (INSERT/UPDATE/DELETE).
=======
        Ejecuta una consulta SQL personalizada.

        Parámetros:
            consulta (str): consulta SQL.
            params (Iterable): parámetros opcionales.
            fetch_all (bool): si es True, retorna todas las filas como diccionarios.
            fetch_one (bool): si es True, retorna una sola fila como diccionario.

        Retorna:
            - Lista de diccionarios (si fetch_all=True).
            - Diccionario (si fetch_one=True).
            - None (si es una operación tipo INSERT sin RETURNING).
>>>>>>> practicas
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

<<<<<<< HEAD
            # Para operaciones que no retornan (ej. INSERT sin RETURNING)
            return None
=======
            return None
>>>>>>> practicas
