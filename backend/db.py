import psycopg2
from psycopg2 import pool
from config import Config

_pool = None

def iniciar_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(
            1, 10,
            host=Config.PG_HOST, port=Config.PG_PORT,
            dbname=Config.PG_DB, user=Config.PG_USER, password=Config.PG_PASS
        )

def obtener_conexion():
    if _pool is None:
        iniciar_pool()
    return _pool.getconn()

def liberar_conexion(conn):
    if _pool:
        _pool.putconn(conn)