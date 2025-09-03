"""Script de diagnóstico completo para problemas de encoding con PostgreSQL"""

import os
import sys
import locale
import psycopg2
from dotenv import load_dotenv

def diagnose_system():
    """Diagnosticar configuración del sistema"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 60)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"Locale: {locale.getlocale()}")
    print(f"Preferred encoding: {locale.getpreferredencoding()}")
    print()

def diagnose_env_file():
    """Diagnosticar archivo .env"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO ARCHIVO .env")
    print("=" * 60)
    
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ Archivo .env no encontrado")
        return
    
    # Leer archivo en bytes para ver encoding real
    with open(env_path, 'rb') as f:
        raw_content = f.read()
    
    print(f"Tamaño del archivo: {len(raw_content)} bytes")
    print(f"Primeros 100 bytes (hex): {raw_content[:100].hex()}")
    
    # Intentar decodificar con diferentes encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    
    for enc in encodings:
        try:
            decoded = raw_content.decode(enc)
            print(f"✅ Decodificación exitosa con {enc}")
            print(f"Contenido:\n{decoded}")
            break
        except UnicodeDecodeError as e:
            print(f"❌ Error con {enc}: {e}")
    
    print()

def diagnose_env_vars():
    """Diagnosticar variables de entorno"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO VARIABLES DE ENTORNO")
    print("=" * 60)
    
    # Cargar con diferentes métodos
    methods = [
        ("Sin encoding", lambda: load_dotenv()),
        ("UTF-8", lambda: load_dotenv(encoding='utf-8')),
        ("Latin-1", lambda: load_dotenv(encoding='latin-1')),
        ("CP1252", lambda: load_dotenv(encoding='cp1252')),
    ]
    
    for method_name, load_func in methods:
        try:
            print(f"\n--- {method_name} ---")
            load_func()
            
            vars_to_check = ['PG_HOST', 'PG_PORT', 'PG_DB', 'PG_USER', 'PG_PASS']
            for var in vars_to_check:
                value = os.getenv(var)
                if value:
                    print(f"{var}: {repr(value)} (len: {len(value)})")
                    # Verificar si hay caracteres problemáticos
                    for i, char in enumerate(value):
                        if ord(char) > 127:
                            print(f"  ⚠️  Carácter no-ASCII en posición {i}: {repr(char)} (ord: {ord(char)})")
            
        except Exception as e:
            print(f"❌ Error con {method_name}: {e}")

def test_raw_connection():
    """Probar conexión cruda sin pool"""
    print("=" * 60)
    print("🔍 TEST CONEXIÓN DIRECTA")
    print("=" * 60)
    
    # Cargar variables de la forma más segura
    load_dotenv(encoding='latin-1')  # Más permisivo
    
    host = os.getenv('PG_HOST', 'localhost')
    port = int(os.getenv('PG_PORT', '5433'))
    database = os.getenv('PG_DB', 'BDTJM')
    user = os.getenv('PG_USER', 'postgres')
    password = os.getenv('PG_PASS', 'root')
    
    print(f"Conexión con: host={host}, port={port}, db={database}, user={user}")
    
    # Métodos de conexión a probar
    connection_methods = [
        {
            'name': 'Parámetros básicos',
            'params': {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
        },
        {
            'name': 'Con client_encoding',
            'params': {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password,
                'client_encoding': 'utf8'
            }
        },
        {
            'name': 'Con options',
            'params': {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password,
                'options': '-c client_encoding=utf8'
            }
        },
        {
            'name': 'DSN simple',
            'dsn': f"host={host} port={port} dbname={database} user={user} password={password}"
        },
        {
            'name': 'DSN con encoding',
            'dsn': f"host={host} port={port} dbname={database} user={user} password={password} client_encoding=utf8"
        }
    ]
    
    for method in connection_methods:
        print(f"\n--- {method['name']} ---")
        try:
            if 'dsn' in method:
                print(f"DSN: {method['dsn']}")
                conn = psycopg2.connect(method['dsn'])
            else:
                print(f"Params: {method['params']}")
                conn = psycopg2.connect(**method['params'])
            
            # Test básico
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"✅ Conexión exitosa!")
                print(f"PostgreSQL: {version[:50]}...")
            
            conn.close()
            print("✅ Conexión cerrada correctamente")
            return  # Si llegamos aquí, ya encontramos una forma que funciona
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Tipo: {type(e)}")
            
            if isinstance(e, UnicodeDecodeError):
                print(f"Posición del error: {e.start}-{e.end}")
                print(f"Bytes problemáticos: {e.object[e.start:e.end]}")

def main():
    """Función principal de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO DE CONEXIÓN POSTGRESQL")
    print("Este script identificará el problema de encoding.\n")
    
    diagnose_system()
    diagnose_env_file()
    diagnose_env_vars()
    test_raw_connection()
    
    print("\n" + "=" * 60)
    print("🔍 RESUMEN")
    print("=" * 60)
    print("Si algún método de conexión funcionó arriba, úsalo en tu aplicación.")
    print("Si no, el problema podría estar en:")
    print("1. Archivo .env con encoding incorrecto")
    print("2. Variables de entorno del sistema con caracteres especiales")
    print("3. Configuración de PostgreSQL")
    print("4. Versión de psycopg2 incompatible")

if __name__ == "__main__":
    main()