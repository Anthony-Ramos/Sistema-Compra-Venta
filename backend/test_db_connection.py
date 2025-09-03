import psycopg2
import locale
import os
from backend.config import Config

cfg = Config()

print("🔎 Debug conexión directa con PostgreSQL")
print(f"HOST: {repr(cfg.PG_HOST)}")
print(f"PORT: {repr(cfg.PG_PORT)}")
print(f"DB: {repr(cfg.PG_DB)}")
print(f"USER: {repr(cfg.PG_USER)}")
print(f"PASS: {repr(cfg.PG_PASS)}")

print(f"🌐 Locale actual: {locale.getlocale()}")
print(f"🌐 Encoding preferido: {locale.getpreferredencoding()}")

# 🔧 Forzar variables de entorno
os.environ["PGCLIENTENCODING"] = "LATIN1"
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    # 🔄 Conexión inicial en LATIN1
    conn = psycopg2.connect(
        host=cfg.PG_HOST,
        port=cfg.PG_PORT,
        database=cfg.PG_DB,
        user=cfg.PG_USER,
        password=cfg.PG_PASS,
        options="-c client_encoding=LATIN1"
    )
    print("✅ Conexión establecida en LATIN1")

    # 🔄 Forzar cambio a UTF8 ya conectados
    conn.set_client_encoding("UTF8")
    print("🔄 Encoding cambiado a UTF8")

    with conn.cursor() as cur:
        cur.execute("SHOW client_encoding")
        print("📋 Encoding final:", cur.fetchone()[0])

        # 🔤 Test caracteres
        cur.execute("SELECT 'áéíóú ñ ÁÉÍÓÚ Ñ'")
        print("🔤 Resultado prueba:", cur.fetchone()[0])

    conn.close()

except Exception as e:
    print("❌ Error al conectar:", type(e).__name__, "->", e)
